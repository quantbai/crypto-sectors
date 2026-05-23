"""
compute_validation.py
=====================

Empirically validates the classification by checking that assets within the same
group co-move more on daily returns than assets in different groups. Produces:

  validation/charts/within_between.png   ← spread bar chart by hierarchy level
  validation/charts/heatmap.png          ← correlation matrix sorted by sector
  validation/charts/ari_vs_ward.png      ← scheme-vs-unsupervised-clustering ARI
  validation/numbers.json                ← machine-readable headline numbers

This is the *only* validation script. It runs in < 30 seconds, uses standard
libraries, and is meant to be re-run on every release.

Run:
    python scripts/compute_validation.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from sklearn.metrics import adjusted_rand_score

ROOT = Path(__file__).resolve().parent.parent
RETURNS = ROOT / "data" / "daily_returns.parquet"
SNAPSHOT = ROOT / "classification" / "snapshot.csv"
CHARTS = ROOT / "validation" / "charts"
NUMBERS = ROOT / "validation" / "numbers.json"

SCHEMES = ["class_code", "sector_code", "sub_sector_code"]


def cross_sectional_demean(returns: pd.DataFrame) -> pd.DataFrame:
    """Subtract the cross-sectional mean from each day — removes market beta."""
    return returns.sub(returns.mean(axis=1), axis=0)


def group_spread(corr: pd.DataFrame, labels: pd.Series) -> tuple[float, float, float]:
    """Compute mean within-group corr, mean between-group corr, and the spread.

    Excludes the diagonal of corr (self-correlation).
    """
    n = corr.shape[0]
    idx = corr.index
    label_arr = labels.reindex(idx).values
    within_sum, within_n = 0.0, 0
    between_sum, between_n = 0.0, 0
    for i in range(n):
        for j in range(i + 1, n):
            li, lj = label_arr[i], label_arr[j]
            if pd.isna(li) or pd.isna(lj):
                continue
            c = corr.iat[i, j]
            if pd.isna(c):
                continue
            if li == lj:
                within_sum += c
                within_n += 1
            else:
                between_sum += c
                between_n += 1
    w = within_sum / max(within_n, 1)
    b = between_sum / max(between_n, 1)
    return w, b, w - b


def random_baseline(corr: pd.DataFrame, labels: pd.Series, n_perm: int = 500,
                    seed: int = 0) -> tuple[float, float]:
    """Mean and 95th-percentile spread under label permutation (null distribution)."""
    rng = np.random.default_rng(seed)
    label_arr = labels.reindex(corr.index).values
    spreads = []
    for _ in range(n_perm):
        permuted = pd.Series(rng.permutation(label_arr), index=corr.index)
        _, _, spread = group_spread(corr, permuted)
        spreads.append(spread)
    return float(np.mean(spreads)), float(np.percentile(spreads, 95))


def ari_vs_ward(corr: pd.DataFrame, labels: pd.Series, k: int) -> float:
    """Adjusted Rand Index between our labels and Ward-linkage clusters at k clusters.

    NaN correlations (insufficient overlap between two asset return series) are
    filled with 0 — equivalent to assuming independence, which is the most
    conservative default for clustering.
    """
    corr_clean = corr.clip(-1, 1).fillna(0)
    dist = np.sqrt(2 * (1 - corr_clean))
    np.fill_diagonal(dist.values, 0)
    # Symmetrize defensively (corr is symmetric but floating-point round-off can break it)
    dist_arr = (dist.values + dist.values.T) / 2
    condensed = squareform(dist_arr, checks=False)
    Z = linkage(condensed, method="ward")
    ward_labels = fcluster(Z, t=k, criterion="maxclust")
    return float(adjusted_rand_score(labels.reindex(corr.index).fillna(-1), ward_labels))


def main() -> int:
    if not RETURNS.exists() or not SNAPSHOT.exists():
        print("[ERROR] Missing inputs.", file=sys.stderr)
        return 1

    CHARTS.mkdir(parents=True, exist_ok=True)

    returns = pd.read_parquet(RETURNS)
    returns.index = pd.to_datetime(returns.index)
    snap = pd.read_csv(SNAPSHOT)

    sym_to_aid = dict(zip(snap.symbol, snap.asset_id))
    keep = [c for c in returns.columns if c in sym_to_aid]
    returns = returns[keep]
    returns.columns = pd.Index([sym_to_aid[c] for c in keep])

    print(f"Validating on {returns.shape[1]} assets × {returns.shape[0]} days")

    # Cross-sectional demean before correlation — removes market beta
    demeaned = cross_sectional_demean(returns)
    corr = demeaned.corr()

    snap_idx = snap.set_index("asset_id")
    results: dict[str, dict] = {}

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bar_data = []
    labels_present: dict[str, pd.Series] = {}
    for scheme in SCHEMES:
        labels = snap_idx[scheme]
        labels_present[scheme] = labels
        w, b, spread = group_spread(corr, labels)
        rb_mean, rb_p95 = random_baseline(corr, labels, n_perm=300)
        n_groups = int(labels.dropna().nunique())
        results[scheme] = {
            "within_corr": round(w, 4),
            "between_corr": round(b, 4),
            "spread": round(spread, 4),
            "random_baseline_mean": round(rb_mean, 4),
            "random_baseline_p95": round(rb_p95, 4),
            "n_groups": n_groups,
            "passes": bool(spread > rb_p95),
        }
        bar_data.append((scheme, w, b, spread, rb_p95))
        print(f"  {scheme:18s}  within={w:+.4f}  between={b:+.4f}  spread={spread:+.4f}  "
              f"random_p95={rb_p95:+.4f}  pass={spread > rb_p95}")

    # Chart 1: within vs between by scheme
    names = [s[0].replace("_code", "") for s in bar_data]
    spreads = [s[3] for s in bar_data]
    p95s = [s[4] for s in bar_data]
    x = np.arange(len(names))
    ax.bar(x - 0.2, spreads, 0.4, label="Spread (within − between)", color="#2e7d32")
    ax.bar(x + 0.2, p95s, 0.4, label="Random-baseline p95", color="#c62828", alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("Mean correlation spread")
    ax.set_title("Within-group vs between-group correlation (post cross-sectional demean)")
    ax.axhline(0, color="black", linewidth=0.5)
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHARTS / "within_between.png", dpi=130)
    plt.close(fig)
    print(f"  wrote {CHARTS / 'within_between.png'}")

    # Chart 2: ARI vs Ward
    fig, ax = plt.subplots(figsize=(7, 4))
    ari_data = []
    for scheme in SCHEMES:
        labels = labels_present[scheme]
        k = int(labels.dropna().nunique())
        if k < 2:
            continue
        ari = ari_vs_ward(corr, labels, k)
        ari_data.append((scheme.replace("_code", ""), k, ari))
        results[scheme]["ari_vs_ward"] = round(ari, 4)
        print(f"  ARI {scheme:18s}  k={k}  ARI={ari:+.4f}")
    if ari_data:
        names_a = [r[0] for r in ari_data]
        vals_a = [r[2] for r in ari_data]
        ax.bar(names_a, vals_a, color="#1565c0")
        ax.set_ylabel("Adjusted Rand Index vs Ward (1-corr)")
        ax.set_title("Agreement with unsupervised clustering")
        ax.axhline(0, color="black", linewidth=0.5)
        ax.set_ylim(-0.05, max(0.5, max(vals_a) * 1.2))
        fig.tight_layout()
        fig.savefig(CHARTS / "ari_vs_ward.png", dpi=130)
        plt.close(fig)
        print(f"  wrote {CHARTS / 'ari_vs_ward.png'}")

    # Chart 3: sorted correlation heatmap by sector
    sector = snap_idx["sector_code"].reindex(corr.index)
    order = sector.sort_values().index
    corr_sorted = corr.loc[order, order]
    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(corr_sorted.values, cmap="RdBu_r", vmin=-0.4, vmax=0.8, aspect="auto")
    ax.set_title("Daily-return correlation matrix sorted by sector")
    ax.set_xticks([])
    ax.set_yticks([])
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Cross-sectionally demeaned return correlation")
    # Sector dividers
    sector_sorted = sector.loc[order]
    boundaries = []
    last = None
    for i, s in enumerate(sector_sorted):
        if s != last and last is not None:
            boundaries.append(i)
        last = s
    for b in boundaries:
        ax.axhline(b - 0.5, color="black", linewidth=0.3, alpha=0.5)
        ax.axvline(b - 0.5, color="black", linewidth=0.3, alpha=0.5)
    fig.tight_layout()
    fig.savefig(CHARTS / "heatmap.png", dpi=130)
    plt.close(fig)
    print(f"  wrote {CHARTS / 'heatmap.png'}")

    NUMBERS.parent.mkdir(parents=True, exist_ok=True)
    NUMBERS.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"  wrote {NUMBERS}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
