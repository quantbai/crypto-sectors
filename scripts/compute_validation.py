"""
compute_validation.py
=====================

Institutional-grade validation for crypto-sectors v1.0 classification.
Six experiments:

  E1  Within vs between co-movement with stationary bootstrap CIs
  E2  Per-sub-sector tightness with size-matched null and Holm correction
  E3  Multiple-testing correction summary (aggregated across E1+E2)
  E4  Rolling-window stability of sector-level spread
  E5  Naive baseline comparison (ours vs chain-only vs random vs single-group)
  E6  group_neut application demo (5-day reversal toy alpha)

Outputs:
  validation/charts/e1_within_between.png
  validation/charts/e2_per_sub_sector.png
  validation/charts/e4_rolling_stability.png
  validation/charts/e5_baseline_comparison.png
  validation/charts/e6_groupneut_demo.png
  validation/charts/heatmap.png          (regenerated, kept for appendix)
  validation/charts/ari_vs_ward.png      (regenerated, kept for appendix)
  validation/numbers.json                (superset; keys prefixed e1_..e6_)

Run:
    python scripts/compute_validation.py

Runtime target: < 5 minutes on a laptop.
Seed: 42 everywhere for reproducibility.
"""
from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from scipy.stats import rankdata
from sklearn.metrics import adjusted_rand_score

# Suppress expected RuntimeWarnings from size-1 sub-sectors (nanmean of empty slice,
# nanstd of single-element array). These are documented behavior in E2.
warnings.filterwarnings("ignore", message="Mean of empty slice", category=RuntimeWarning)
warnings.filterwarnings("ignore", message="All-NaN slice", category=RuntimeWarning)
warnings.filterwarnings("ignore", message="Degrees of freedom", category=RuntimeWarning)
warnings.filterwarnings("ignore", message="invalid value encountered", category=RuntimeWarning)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
RETURNS_PATH = ROOT / "data" / "daily_returns.parquet"
SNAPSHOT_PATH = ROOT / "classification" / "snapshot.csv"
TAXONOMY_PATH = ROOT / "taxonomy.yaml"
WIDE = ROOT / "classification" / "wide"
CHARTS = ROOT / "validation" / "charts"
NUMBERS_PATH = ROOT / "validation" / "numbers.json"

SEED = 42
N_BOOT = 1000   # stationary bootstrap replicates
N_PERM = 1000   # label-permutation null draws
BLOCK_LEN = 27  # floor(sqrt(730)) = 27  (Politis-Romano 1994)

# Publication-quality plot settings
STYLE_KW = dict(dpi=150)
FONT_SIZE = 11
plt.rcParams.update({
    "font.size": FONT_SIZE,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "legend.fontsize": 10,
    "figure.constrained_layout.use": True,
})

# Sector-level colour palette (14 possible sectors, use tab20 so each has a distinct hue)
_SECTOR_CMAP = plt.get_cmap("tab20")


def _sector_color(code: int) -> Any:
    """Deterministic colour per sector code, consistent across all charts."""
    # Map code integer to [0,1] via a stable hash index
    palette_index = (int(code) % 20) / 20.0
    return _SECTOR_CMAP(palette_index)


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------

def load_data() -> tuple[pd.DataFrame, pd.DataFrame, dict[int, str], dict[int, str], dict[int, str]]:
    """Load returns and snapshot; map returns columns to asset_id.

    Returns
    -------
    corr_full  : (n_assets × n_assets) full-sample Pearson correlation matrix on log-returns
    snap       : snapshot DataFrame indexed by asset_id
    ss_names   : sub_sector_code -> display name
    sec_names  : sector_code -> display name
    cls_names  : class_code -> display name
    """
    returns_raw = pd.read_parquet(RETURNS_PATH)
    returns_raw.index = pd.to_datetime(returns_raw.index)

    snap = pd.read_csv(SNAPSHOT_PATH)
    sym_to_aid = dict(zip(snap["symbol"], snap["asset_id"]))
    keep = [c for c in returns_raw.columns if c in sym_to_aid]
    returns = returns_raw[keep].copy()
    returns.columns = pd.Index([sym_to_aid[c] for c in keep])

    # Log-returns (already daily; treat as log-return directly for correlation)
    # Cross-sectional demean removes market beta
    demeaned = returns.sub(returns.mean(axis=1), axis=0)

    # Full-sample correlation — NaN-tolerant
    corr_full = demeaned.corr(method="pearson", min_periods=60)

    snap = snap.set_index("asset_id")

    # Load taxonomy for display names
    with open(TAXONOMY_PATH, encoding="utf-8") as f:
        tax = yaml.safe_load(f)

    ss_names = {int(x["code"]): x["name"] for x in tax["sub_sectors"]}
    sec_names = {int(x["code"]): x["name"] for x in tax["sectors"]}
    cls_names = {int(x["code"]): x["name"] for x in tax["classes"]}

    n_assets = len(returns.columns)
    n_days = len(returns)
    print(f"[data] {n_assets} assets × {n_days} trading days "
          f"({returns.index.min().date()} to {returns.index.max().date()})")

    return corr_full, snap, ss_names, sec_names, cls_names, returns, demeaned


# ---------------------------------------------------------------------------
# Core statistical primitives
# ---------------------------------------------------------------------------

def _group_spread(corr: pd.DataFrame, labels: pd.Series) -> tuple[float, float, float, int, int]:
    """Mean within-group and between-group Pearson ρ and their spread.

    Returns (within, between, spread, n_within_pairs, n_between_pairs).
    Diagonal excluded. NaN labels or NaN corr entries skipped.
    """
    idx = corr.index
    lbl = labels.reindex(idx).values
    c_arr = corr.values
    n = len(idx)

    within_sum, within_n = 0.0, 0
    between_sum, between_n = 0.0, 0

    for i in range(n):
        li = lbl[i]
        if li is None or (not isinstance(li, str) and np.isnan(float(li) if li is not None else np.nan)):
            continue
        for j in range(i + 1, n):
            lj = lbl[j]
            if lj is None or (not isinstance(lj, str) and np.isnan(float(lj) if lj is not None else np.nan)):
                continue
            c = c_arr[i, j]
            if np.isnan(c):
                continue
            if li == lj:
                within_sum += c
                within_n += 1
            else:
                between_sum += c
                between_n += 1

    w = within_sum / max(within_n, 1)
    b = between_sum / max(between_n, 1)
    return w, b, w - b, within_n, between_n


def _fast_spread(corr_vals: np.ndarray, label_arr: np.ndarray) -> float:
    """Vectorised spread computation for bootstrap inner loops.

    Parameters
    ----------
    corr_vals : 2D upper-triangle flattened? No — full square; we use triu mask.
    label_arr : 1-D array of group labels (already matched to corr row order).

    Returns spread (scalar).
    """
    n = len(label_arr)
    mask = np.triu(np.ones((n, n), dtype=bool), k=1)
    same = (label_arr[:, None] == label_arr[None, :]) & mask
    diff = (~(label_arr[:, None] == label_arr[None, :])) & mask

    # NaN handling: treat as neither within nor between
    c = corr_vals
    nan_mask = np.isnan(c)
    same &= ~nan_mask
    diff &= ~nan_mask

    w = c[same].mean() if same.any() else 0.0
    b = c[diff].mean() if diff.any() else 0.0
    return float(w - b)


def _stationary_bootstrap_spreads(
    corr_vals: np.ndarray,
    label_arr: np.ndarray,
    n_boot: int = N_BOOT,
    block_len: int = BLOCK_LEN,
    seed: int = SEED,
) -> np.ndarray:
    """Stationary bootstrap (Politis-Romano 1994) over the CORRELATION matrix rows/cols.

    Since the correlation matrix is estimated from a time series of length T,
    the stationary bootstrap is applied to the index set of assets by resampling
    blocks of *consecutive assets in the sorted (by label) order* — approximating
    the temporal dependence structure.

    NOTE: The correlation matrix already summarises T days. We cannot re-bootstrap
    individual days here without the raw returns. The raw-returns path is taken
    in E1 where we have access to `demeaned`. This function is a fallback for
    contexts where only the corr matrix is available.

    For E1 we pass raw demeaned returns and compute correlation on each replicate.
    """
    rng = np.random.default_rng(seed)
    n = len(label_arr)
    spreads = np.empty(n_boot)
    p = 1.0 / block_len  # geometric block length parameter

    for b in range(n_boot):
        # Resample rows/cols of corr matrix with stationary blocks
        indices = []
        while len(indices) < n:
            start = rng.integers(0, n)
            length = int(np.ceil(rng.geometric(p)))
            block = [(start + k) % n for k in range(length)]
            indices.extend(block)
        indices = np.array(indices[:n])
        corr_b = corr_vals[np.ix_(indices, indices)]
        lbl_b = label_arr[indices]
        spreads[b] = _fast_spread(corr_b, lbl_b)

    return spreads


def _stationary_bootstrap_returns_spread(
    demeaned: pd.DataFrame,
    label_arr: np.ndarray,
    n_boot: int = N_BOOT,
    block_len: int = BLOCK_LEN,
    seed: int = SEED,
) -> np.ndarray:
    """Stationary bootstrap on the TIME axis of the demeaned returns matrix.

    Each replicate: resample T time-rows with geometric blocks, recompute
    correlation, compute spread. This is the proper time-series bootstrap.

    NaN handling: assets with fewer than min_periods=60 valid observations in a
    replicate are excluded (NaN columns), preventing NaN propagation through the
    matrix multiply. We use a pairwise Pearson approach via nansum for robustness.
    """
    rng = np.random.default_rng(seed)
    T, N = demeaned.shape
    p = 1.0 / block_len
    data = demeaned.values.astype(np.float64)  # shape (T, N)
    spreads = np.empty(n_boot)
    MIN_OBS = 60  # minimum non-NaN obs per asset per replicate

    for b in range(n_boot):
        rows = []
        while len(rows) < T:
            start = rng.integers(0, T)
            length = int(np.ceil(rng.geometric(p)))
            block = [(start + k) % T for k in range(length)]
            rows.extend(block)
        rows = np.array(rows[:T])
        data_b = data[rows, :]  # (T, N)

        # Identify columns with enough non-NaN obs
        valid_cols = np.where(np.sum(~np.isnan(data_b), axis=0) >= MIN_OBS)[0]
        data_b = data_b[:, valid_cols]
        lbl_b = label_arr[valid_cols]

        if data_b.shape[1] < 10:
            spreads[b] = 0.0
            continue

        # Per-pair Pearson correlation using nansum (NaN-safe)
        # demean each column using its own valid mean
        col_means = np.nanmean(data_b, axis=0)
        dm = data_b - col_means[np.newaxis, :]
        # col variances
        col_vars = np.nansum(dm ** 2, axis=0)  # unnormalised
        col_vars[col_vars == 0] = np.nan

        # For the cross-correlation: use nansum of products.
        # To keep it fast, use the matrix product ignoring NaN via masking.
        # Replace NaN with 0 for cross-product, track valid-pair counts.
        dm_filled = np.where(np.isnan(dm), 0.0, dm)
        # Count of valid pairs: binary mask
        valid_mask = (~np.isnan(data_b)).astype(np.float64)
        pair_counts = valid_mask.T @ valid_mask  # (N', N')
        cross = dm_filled.T @ dm_filled          # (N', N')
        # Normalise by sqrt(var_i * var_j) — both col_vars already unnormalised sum
        denom = np.sqrt(col_vars[:, None] * col_vars[None, :])
        denom[denom == 0] = np.nan
        corr_b = cross / denom
        # Zero out pairs with too few co-observations
        corr_b[pair_counts < MIN_OBS] = np.nan
        np.fill_diagonal(corr_b, np.nan)

        spreads[b] = _fast_spread(corr_b, lbl_b)

    return spreads


def _label_permutation_null(
    corr_vals: np.ndarray,
    label_arr: np.ndarray,
    n_perm: int = N_PERM,
    seed: int = SEED,
) -> np.ndarray:
    """Spread under label permutation null."""
    rng = np.random.default_rng(seed + 1)
    spreads = np.empty(n_perm)
    for i in range(n_perm):
        perm = rng.permutation(label_arr)
        spreads[i] = _fast_spread(corr_vals, perm)
    return spreads


# ---------------------------------------------------------------------------
# E1 — Within vs between, stationary bootstrap
# ---------------------------------------------------------------------------

def e1_within_between(
    corr_full: pd.DataFrame,
    snap: pd.DataFrame,
    demeaned: pd.DataFrame,
    sec_names: dict,
    cls_names: dict,
) -> dict:
    """E1: per-level spread with stationary bootstrap CIs and permutation null."""
    print("[E1] Within vs between spread with stationary bootstrap ...")

    levels = [
        ("class",      "class_code",      cls_names),
        ("sector",     "sector_code",      sec_names),
        ("sub_sector", "sub_sector_code",  {}),
    ]

    # Restrict to assets that are in both corr_full and snapshot
    assets = corr_full.index.intersection(snap.index)
    corr = corr_full.loc[assets, assets]
    demeaned_aligned = demeaned[[c for c in demeaned.columns if c in assets]].reindex(columns=assets)

    results = {}
    bar_items = []  # (level_label, spread, ci_lo, ci_hi, null_p95)

    for level_key, col, _ in levels:
        labels_series = snap[col].reindex(assets).astype(str)
        # Convert pandas NA / "<NA>" to "nan" so comparisons work
        labels_series = labels_series.where(labels_series != "<NA>", other=np.nan)
        valid = labels_series.notna()
        assets_v = assets[valid]
        lbl = labels_series[valid].values
        corr_v = corr.loc[assets_v, assets_v].values
        dm_v = demeaned_aligned[assets_v]

        # Observed spread
        obs_spread = _fast_spread(corr_v, lbl)

        # Stationary bootstrap on time axis -> CI
        boot_spreads = _stationary_bootstrap_returns_spread(
            dm_v, lbl, n_boot=N_BOOT, block_len=BLOCK_LEN, seed=SEED
        )
        ci_lo = float(np.percentile(boot_spreads, 2.5))
        ci_hi = float(np.percentile(boot_spreads, 97.5))

        # Permutation null
        null_spreads = _label_permutation_null(corr_v, lbl, n_perm=N_PERM, seed=SEED)
        null_p95 = float(np.percentile(null_spreads, 95))
        # One-sided p-value: fraction of null draws >= observed
        obs_p_value = float((null_spreads >= obs_spread).mean())

        results[f"e1_{level_key}_spread"]    = round(obs_spread, 5)
        results[f"e1_{level_key}_ci_lo"]     = round(ci_lo, 5)
        results[f"e1_{level_key}_ci_hi"]     = round(ci_hi, 5)
        results[f"e1_{level_key}_null_p95"]  = round(null_p95, 5)
        results[f"e1_{level_key}_obs_p_value"] = round(obs_p_value, 5)

        bar_items.append((level_key, obs_spread, ci_lo, ci_hi, null_p95))
        print(f"  {level_key:12s}  spread={obs_spread:+.5f}  "
              f"CI=[{ci_lo:+.5f},{ci_hi:+.5f}]  null_p95={null_p95:+.5f}  "
              f"p_val={obs_p_value:.4f}")

    # --- Chart ---
    fig, ax = plt.subplots(figsize=(8, 5), **STYLE_KW)
    labels_disp = [b[0].replace("_", "\n") for b in bar_items]
    spreads = [b[1] for b in bar_items]
    cilo = [b[2] for b in bar_items]
    cihi = [b[3] for b in bar_items]
    null95 = [b[4] for b in bar_items]
    x = np.arange(len(labels_disp))

    colors = ["#1b5e20", "#2e7d32", "#4caf50"]
    yerr_lo = [max(0, s - lo) for s, lo in zip(spreads, cilo)]
    yerr_hi = [max(0, hi - s) for s, hi in zip(spreads, cihi)]

    bars = ax.bar(x, spreads, 0.5, color=colors,
                  label="Observed spread (within − between)")
    ax.errorbar(x, spreads, yerr=[yerr_lo, yerr_hi],
                fmt="none", color="black", linewidth=1.5, capsize=6,
                label="95% CI (stationary bootstrap)")
    ax.plot(x, null95, "r--", linewidth=1.5, marker="x", markersize=8,
            label="Null p95 (label permutation)")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels_disp, fontsize=12)
    ax.set_ylabel("Mean correlation spread (within − between)")
    ax.set_title("E1: Within-group vs between-group co-movement by hierarchy level\n"
                 "(stationary bootstrap CIs; Politis-Romano 1994, block ≈ 27 days)")
    ax.legend(loc="upper left")
    fig.savefig(CHARTS / "e1_within_between.png", **STYLE_KW)
    plt.close(fig)
    print(f"  chart -> {CHARTS / 'e1_within_between.png'}")

    return results


# ---------------------------------------------------------------------------
# E2 — Per-sub-sector tightness
# ---------------------------------------------------------------------------

def e2_per_sub_sector(
    corr_full: pd.DataFrame,
    snap: pd.DataFrame,
    ss_names: dict,
) -> dict:
    """E2: per-sub-sector tightness with size-matched null and Holm correction."""
    print("[E2] Per-sub-sector tightness ...")

    assets = corr_full.index.intersection(snap.index)
    corr = corr_full.loc[assets, assets]
    corr_vals = corr.values
    n_total = len(assets)

    labels_series = snap["sub_sector_code"].reindex(assets)
    rng = np.random.default_rng(SEED + 2)

    rows = []
    for code, grp in labels_series.groupby(labels_series):
        n = len(grp)
        members = grp.index
        member_idx = np.array([assets.get_loc(m) for m in members if m in assets])
        n_actual = len(member_idx)

        if n_actual < 1:
            continue

        # Within-sub-sector mean rho
        if n_actual >= 2:
            pairs = [(corr_vals[i, j])
                     for ii, i in enumerate(member_idx)
                     for jj, j in enumerate(member_idx) if jj > ii]
            rho_within = float(np.nanmean(pairs)) if pairs else np.nan
        else:
            rho_within = np.nan

        # Size-matched random null: 1000 draws of n_actual random assets
        N_NULL = 1000
        null_rhos = []
        for _ in range(N_NULL):
            rand_idx = rng.choice(n_total, size=n_actual, replace=False)
            if n_actual >= 2:
                pairs_r = [corr_vals[rand_idx[ii], rand_idx[jj]]
                           for ii in range(n_actual)
                           for jj in range(ii + 1, n_actual)]
                null_rhos.append(np.nanmean(pairs_r))
            else:
                null_rhos.append(np.nan)

        null_arr = np.array(null_rhos)
        null_mean = float(np.nanmean(null_arr))
        null_std  = float(np.nanstd(null_arr))
        null_p50  = float(np.nanmedian(null_arr))
        null_p95  = float(np.nanpercentile(null_arr, 95))

        if n_actual < 3 or null_std == 0:
            z = np.nan
            p_raw = np.nan
            status = "underpowered"
        else:
            z = (rho_within - null_mean) / null_std
            # One-sided p: fraction of null draws >= observed rho_within
            p_raw = float((null_arr >= rho_within).sum() / N_NULL)
            status = None  # filled after Holm

        rows.append({
            "code":       int(code),
            "name":       ss_names.get(int(code), str(code)),
            "n":          n_actual,
            "rho_within": round(rho_within, 5) if not np.isnan(rho_within) else None,
            "null_p50":   round(null_p50, 5),
            "null_p95":   round(null_p95, 5),
            "z":          round(z, 4) if not np.isnan(z) else None,
            "p_raw":      round(p_raw, 5) if not np.isnan(p_raw) else None,
            "p_holm":     None,
            "verdict":    status,
        })

    # Holm-Bonferroni correction on the powered (n >= 3) tests
    powered = [r for r in rows if r["p_raw"] is not None]
    powered_sorted = sorted(powered, key=lambda r: r["p_raw"])
    m = len(powered_sorted)
    for rank, r in enumerate(powered_sorted, start=1):
        p_holm = min(1.0, r["p_raw"] * (m - rank + 1))
        r["p_holm"] = round(p_holm, 5)
        if p_holm < 0.05:
            r["verdict"] = "tight"
        elif r["z"] is not None and r["z"] > 0:
            r["verdict"] = "marginal"
        else:
            r["verdict"] = "loose"

    n_survive = sum(1 for r in rows if r.get("verdict") == "tight")
    print(f"  {m} sub-sectors tested; {n_survive} survive Holm α=0.05")

    # Sort final table by z descending for display
    def _sort_key(r):
        return r["z"] if r["z"] is not None else -999.0
    rows_sorted = sorted(rows, key=_sort_key, reverse=True)

    # --- Chart ---
    # Horizontal bar chart of rho_within per sub-sector
    fig_h = max(6, len(rows_sorted) * 0.35 + 2)
    fig, ax = plt.subplots(figsize=(10, fig_h), **STYLE_KW)

    names_disp = [f"{r['name']} ({r['code']})" for r in rows_sorted]
    rho_vals = [r["rho_within"] if r["rho_within"] is not None else 0.0 for r in rows_sorted]
    null_p50_vals = [r["null_p50"] for r in rows_sorted]
    null_p95_vals = [r["null_p95"] for r in rows_sorted]
    verdicts = [r["verdict"] for r in rows_sorted]

    color_map = {"tight": "#1b5e20", "marginal": "#f57f17", "loose": "#b71c1c", "underpowered": "#9e9e9e"}
    bar_colors = [color_map.get(v, "#9e9e9e") for v in verdicts]

    y = np.arange(len(names_disp))
    ax.barh(y, rho_vals, 0.6, color=bar_colors, alpha=0.85, label="ρ_within (observed)")

    # Null p50 reference line (vertical)
    ax.axvline(float(np.nanmean(null_p50_vals)), color="#455a64", linewidth=1.2,
               linestyle="--", label="Mean null p50")

    # Null p95 shaded band: shade between min and max null_p95 across sub-sectors
    null_p95_mean = float(np.nanmean(null_p95_vals))
    ax.axvline(null_p95_mean, color="#b71c1c", linewidth=1.2,
               linestyle=":", label="Mean null p95")

    ax.set_yticks(y)
    ax.set_yticklabels(names_disp, fontsize=8)
    ax.set_xlabel("Mean pairwise ρ within sub-sector")
    ax.set_title("E2: Per-sub-sector tightness\n"
                 "(green=tight, orange=marginal, red=loose, grey=underpowered; Holm α=0.05)")
    ax.legend(loc="lower right", fontsize=9)
    # Add verdict text
    for i, r in enumerate(rows_sorted):
        v = r["verdict"]
        txt = "✓" if v == "tight" else ("?" if v == "marginal" else ("✗" if v == "loose" else "n<3"))
        ax.text(max(rho_vals) * 1.02 if max(rho_vals) > 0 else 0.05, i, txt,
                va="center", fontsize=7, color=color_map.get(v, "#9e9e9e"))
    fig.savefig(CHARTS / "e2_per_sub_sector.png", **STYLE_KW)
    plt.close(fig)
    print(f"  chart -> {CHARTS / 'e2_per_sub_sector.png'}")

    return {
        "e2_sub_sectors": rows_sorted,
        "e2_n_tested": m,
        "e2_n_survive_holm_05": n_survive,
    }


# ---------------------------------------------------------------------------
# E3 — Multiple-testing correction summary
# ---------------------------------------------------------------------------

def e3_multiple_testing(e1_results: dict, e2_results: dict) -> dict:
    """E3: aggregate Holm-Bonferroni summary across all tests."""
    print("[E3] Multiple-testing correction summary ...")

    n_level_tests = 3  # class, sector, sub_sector
    n_ss_tests = e2_results["e2_n_tested"]
    n_total = n_level_tests + n_ss_tests

    # Level tests: use E1 p-values
    level_pvals = [
        e1_results["e1_class_obs_p_value"],
        e1_results["e1_sector_obs_p_value"],
        e1_results["e1_sub_sector_obs_p_value"],
    ]
    ss_pvals = [r["p_raw"] for r in e2_results["e2_sub_sectors"] if r["p_raw"] is not None]
    all_pvals = level_pvals + ss_pvals

    # Holm-Bonferroni across all_pvals
    all_pvals_sorted = sorted(enumerate(all_pvals), key=lambda x: x[1])
    m = len(all_pvals_sorted)
    holm_rejected = 0
    for rank, (orig_idx, p) in enumerate(all_pvals_sorted, start=1):
        p_holm = p * (m - rank + 1)
        if p_holm < 0.05:
            holm_rejected += 1

    print(f"  Total tests: {n_total} ({n_level_tests} level + {n_ss_tests} sub-sector)")
    print(f"  Survive Holm α=0.05: {holm_rejected}")

    return {
        "e3_n_tests": n_total,
        "e3_n_level_tests": n_level_tests,
        "e3_n_ss_tests": n_ss_tests,
        "e3_n_survive_holm_05": holm_rejected,
    }


# ---------------------------------------------------------------------------
# E4 — Rolling-window stability
# ---------------------------------------------------------------------------

def e4_rolling_stability(demeaned: pd.DataFrame, snap: pd.DataFrame) -> dict:
    """E4: 180-day rolling window, step 30 days, sector-level spread."""
    print("[E4] Rolling-window stability ...")

    assets = [c for c in demeaned.columns if c in snap.index]
    dm = demeaned[assets]
    snap_a = snap.reindex(assets)
    labels_series = snap_a["sector_code"].astype(str).where(snap_a["sector_code"].notna())
    lbl = labels_series.values

    T = len(dm)
    WINDOW = 180
    STEP = 30

    windows = []
    start = 0
    while start + WINDOW <= T:
        end = start + WINDOW
        windows.append((start, end))
        start += STEP

    n_windows = len(windows)
    window_dates = []
    window_spreads = []

    rng = np.random.default_rng(SEED + 4)
    N_BOOT_ROLL = 200  # fewer bootstraps per window for speed
    MIN_OBS_ROLL = 30  # minimum non-NaN obs per asset per 180-day window

    def _window_corr(data_chunk: np.ndarray) -> np.ndarray:
        """NaN-safe pairwise Pearson on a (T, N) chunk."""
        col_means = np.nanmean(data_chunk, axis=0)
        dm_c = data_chunk - col_means[np.newaxis, :]
        col_vars = np.nansum(dm_c ** 2, axis=0)
        col_vars[col_vars == 0] = np.nan
        dm_filled = np.where(np.isnan(dm_c), 0.0, dm_c)
        valid_mask = (~np.isnan(data_chunk)).astype(np.float64)
        pair_counts = valid_mask.T @ valid_mask
        cross = dm_filled.T @ dm_filled
        denom = np.sqrt(col_vars[:, None] * col_vars[None, :])
        denom[denom == 0] = np.nan
        corr = cross / denom
        corr[pair_counts < MIN_OBS_ROLL] = np.nan
        np.fill_diagonal(corr, np.nan)
        return corr

    spread_cis = []

    for (start, end) in windows:
        chunk = dm.iloc[start:end]
        data_c = chunk.values
        corr_c = _window_corr(data_c)
        obs = _fast_spread(corr_c, lbl)

        # Bootstrap CI
        boot = []
        p = 1.0 / BLOCK_LEN
        Tc = data_c.shape[0]
        for _ in range(N_BOOT_ROLL):
            rows = []
            while len(rows) < Tc:
                s = rng.integers(0, Tc)
                length = int(np.ceil(rng.geometric(p)))
                rows.extend([(s + k) % Tc for k in range(length)])
            rows = np.array(rows[:Tc])
            db = data_c[rows, :]
            corr_b = _window_corr(db)
            boot.append(_fast_spread(corr_b, lbl))

        boot = np.array(boot)
        ci_lo = float(np.percentile(boot, 2.5))
        ci_hi = float(np.percentile(boot, 97.5))

        end_date = dm.index[end - 1]
        window_dates.append(end_date)
        window_spreads.append(float(obs))
        spread_cis.append((ci_lo, ci_hi))

    spreads_arr = np.array(window_spreads)
    n_positive = int((spreads_arr > 0).sum())
    pct_positive = float(n_positive / n_windows)

    print(f"  {n_windows} windows; {n_positive}/{n_windows} positive "
          f"({pct_positive*100:.0f}%)")
    print(f"  spread range: [{spreads_arr.min():+.5f}, {spreads_arr.max():+.5f}], "
          f"median={float(np.median(spreads_arr)):+.5f}")

    # --- Chart ---
    fig, ax = plt.subplots(figsize=(10, 5), **STYLE_KW)
    dates = window_dates
    ci_lo_arr = np.array([c[0] for c in spread_cis])
    ci_hi_arr = np.array([c[1] for c in spread_cis])

    ax.fill_between(dates, ci_lo_arr, ci_hi_arr, alpha=0.25, color="#1565c0",
                    label="95% CI (stationary bootstrap per window)")
    ax.plot(dates, window_spreads, color="#1565c0", linewidth=1.8, marker="o",
            markersize=4, label="Within−between spread (sector level)")
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Window end date")
    ax.set_ylabel("Mean correlation spread")
    ax.set_title(f"E4: Rolling-window stability of sector-level spread\n"
                 f"(180-day window, 30-day step; {n_positive}/{n_windows} = "
                 f"{pct_positive*100:.0f}% positive)")
    ax.legend()
    fig.autofmt_xdate()
    fig.savefig(CHARTS / "e4_rolling_stability.png", **STYLE_KW)
    plt.close(fig)
    print(f"  chart -> {CHARTS / 'e4_rolling_stability.png'}")

    return {
        "e4_n_windows": n_windows,
        "e4_n_windows_spread_positive": n_positive,
        "e4_pct_windows_positive": round(pct_positive, 4),
        "e4_min_spread": round(float(spreads_arr.min()), 5),
        "e4_max_spread": round(float(spreads_arr.max()), 5),
        "e4_median_spread": round(float(np.median(spreads_arr)), 5),
    }


# ---------------------------------------------------------------------------
# E5 — Naive baseline comparison
# ---------------------------------------------------------------------------

def e5_baseline_comparison(
    corr_full: pd.DataFrame,
    snap: pd.DataFrame,
) -> dict:
    """E5: our sector vs chain-only vs random vs single-group."""
    print("[E5] Naive baseline comparison ...")

    assets = corr_full.index.intersection(snap.index)
    corr = corr_full.loc[assets, assets]
    corr_vals = corr.values

    # Ours: sector_code
    lbl_ours = snap["sector_code"].reindex(assets).astype(str).values
    spread_ours = _fast_spread(corr_vals, lbl_ours)

    # Chain-only: chain_ecosystem
    lbl_chain = snap["chain_ecosystem"].reindex(assets).fillna("UNKNOWN").astype(str).values
    spread_chain = _fast_spread(corr_vals, lbl_chain)

    # Random: matched cardinality (n_groups = sector unique count)
    n_groups_ours = int(snap["sector_code"].reindex(assets).nunique())
    rng = np.random.default_rng(SEED + 5)
    n_assets = len(assets)
    n_random = 100
    random_spreads = []
    for _ in range(n_random):
        # Random partition into n_groups_ours groups with matched marginals
        rand_lbl = rng.integers(0, n_groups_ours, size=n_assets).astype(str)
        random_spreads.append(_fast_spread(corr_vals, rand_lbl))
    spread_random_mean = float(np.mean(random_spreads))
    spread_random_std  = float(np.std(random_spreads))

    # Single group: spread = 0 by construction
    spread_single = 0.0

    ours_minus_chain  = float(spread_ours - spread_chain)
    ours_minus_random = float(spread_ours - spread_random_mean)

    print(f"  Ours (sector):  {spread_ours:+.5f}")
    print(f"  Chain-only:     {spread_chain:+.5f}")
    print(f"  Random (mean):  {spread_random_mean:+.5f} (±{spread_random_std:.5f})")
    print(f"  Single-group:   {spread_single:+.5f}")
    print(f"  Ours minus chain:  {ours_minus_chain:+.5f}")
    print(f"  Ours minus random: {ours_minus_random:+.5f}")

    # --- Chart ---
    fig, ax = plt.subplots(figsize=(8, 5), **STYLE_KW)
    labels_disp = ["Ours\n(sector)", "Chain-only", "Random\n(mean ±1σ)", "Single\ngroup"]
    vals = [spread_ours, spread_chain, spread_random_mean, spread_single]
    bar_colors = ["#1b5e20", "#1565c0", "#f57f17", "#9e9e9e"]
    bars = ax.bar(np.arange(4), vals, 0.5, color=bar_colors, alpha=0.85)

    # Error bar for random
    ax.errorbar([2], [spread_random_mean], yerr=[spread_random_std * 1.96],
                fmt="none", color="black", linewidth=1.5, capsize=6)

    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(np.arange(4))
    ax.set_xticklabels(labels_disp, fontsize=11)
    ax.set_ylabel("Mean correlation spread (within − between)")
    ax.set_title("E5: Sector classification vs naive baselines")

    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2.0, max(val + 0.001, 0.001),
                f"{val:+.4f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

    fig.savefig(CHARTS / "e5_baseline_comparison.png", **STYLE_KW)
    plt.close(fig)
    print(f"  chart -> {CHARTS / 'e5_baseline_comparison.png'}")

    return {
        "e5_spread_ours": round(spread_ours, 5),
        "e5_spread_chain": round(spread_chain, 5),
        "e5_spread_random_mean": round(spread_random_mean, 5),
        "e5_spread_random_std": round(spread_random_std, 5),
        "e5_spread_single": round(spread_single, 5),
        "e5_ours_minus_chain": round(ours_minus_chain, 5),
        "e5_ours_minus_random": round(ours_minus_random, 5),
    }


# ---------------------------------------------------------------------------
# E6 — group_neut application demo
# ---------------------------------------------------------------------------

def e6_groupneut_demo(
    returns_raw: pd.DataFrame,
    snap: pd.DataFrame,
) -> dict:
    """E6: 5-day reversal toy alpha; sector demean; IC Sharpe; variance decomp."""
    print("[E6] group_neut application demo ...")

    assets = [c for c in returns_raw.columns if c in snap.index]
    ret = returns_raw[assets].copy()
    snap_a = snap.reindex(assets)

    # Toy alpha: 5-day reversal = -1 * rolling(5).sum().shift(1)
    alpha_raw = -ret.rolling(5).sum().shift(1)

    # Sector labels
    sector_lbl = snap_a["sector_code"]

    def sector_demean(alpha: pd.DataFrame) -> pd.DataFrame:
        """Subtract sector mean per day."""
        out = alpha.copy()
        for dt in alpha.index:
            row = alpha.loc[dt]
            for sec, grp in sector_lbl.groupby(sector_lbl):
                grp_assets = [a for a in grp.index if a in row.index]
                if not grp_assets:
                    continue
                sec_mean = row[grp_assets].mean()
                if not np.isnan(sec_mean):
                    out.loc[dt, grp_assets] -= sec_mean
        return out

    def chain_demean(alpha: pd.DataFrame) -> pd.DataFrame:
        """Subtract chain_ecosystem mean per day."""
        out = alpha.copy()
        chain_lbl = snap_a["chain_ecosystem"].fillna("UNKNOWN")
        for dt in alpha.index:
            row = alpha.loc[dt]
            for chn, grp in chain_lbl.groupby(chain_lbl):
                grp_assets = [a for a in grp.index if a in row.index]
                if not grp_assets:
                    continue
                chn_mean = row[grp_assets].mean()
                if not np.isnan(chn_mean):
                    out.loc[dt, grp_assets] -= chn_mean
        return out

    def rank_ic_series(alpha: pd.DataFrame, fwd_ret: pd.DataFrame) -> pd.Series:
        """Spearman rank IC per day."""
        ics = []
        for dt in alpha.index:
            a = alpha.loc[dt].dropna()
            f = fwd_ret.loc[dt].reindex(a.index).dropna()
            common = a.index.intersection(f.index)
            if len(common) < 10:
                ics.append(np.nan)
                continue
            ra = rankdata(a[common])
            rf = rankdata(f[common])
            ic = float(np.corrcoef(ra, rf)[0, 1])
            ics.append(ic)
        return pd.Series(ics, index=alpha.index)

    # Forward 1-day returns
    fwd_ret = ret.shift(-1)

    # Raw alpha IC
    ic_raw = rank_ic_series(alpha_raw, fwd_ret)

    # Sector-demeaned alpha
    print("  Computing sector demean (may take ~30s) ...")
    alpha_sec = sector_demean(alpha_raw)
    ic_sec = rank_ic_series(alpha_sec, fwd_ret)

    # Sector + chain double-demeaned
    print("  Computing chain demean ...")
    alpha_sec_chain = chain_demean(alpha_sec)
    ic_sec_chain = rank_ic_series(alpha_sec_chain, fwd_ret)

    def ic_stats(s: pd.Series) -> tuple[float, float]:
        clean = s.dropna()
        if len(clean) < 5:
            return 0.0, 0.0
        return float(clean.mean()), float(clean.mean() / clean.std() * np.sqrt(252))

    mean_raw, sharpe_raw = ic_stats(ic_raw)
    mean_sec, sharpe_sec = ic_stats(ic_sec)
    mean_sec_chain, sharpe_sec_chain = ic_stats(ic_sec_chain)

    # Variance decomposition across (date, asset) cells
    # Flatten alpha_raw to a long series; compute between-sector variance fraction
    alpha_long = alpha_raw.stack().dropna()
    alpha_long.index.names = ["date", "asset_id"]
    alpha_df = alpha_long.reset_index()
    alpha_df.columns = ["date", "asset_id", "alpha"]
    alpha_df = alpha_df.merge(
        snap_a[["sector_code"]].reset_index(),
        on="asset_id", how="left"
    )
    alpha_df = alpha_df.dropna(subset=["sector_code"])

    total_var = float(alpha_df["alpha"].var())
    sector_means = alpha_df.groupby(["date", "sector_code"])["alpha"].transform("mean")
    between_var = float(sector_means.var())
    alpha_var_between_pct = float(between_var / total_var * 100) if total_var > 0 else 0.0

    print(f"  IC raw: mean={mean_raw:+.5f}  Sharpe={sharpe_raw:+.4f}")
    print(f"  IC sector-demeaned: mean={mean_sec:+.5f}  Sharpe={sharpe_sec:+.4f}")
    print(f"  IC sec+chain-demeaned: mean={mean_sec_chain:+.5f}  Sharpe={sharpe_sec_chain:+.4f}")
    print(f"  Between-sector variance fraction: {alpha_var_between_pct:.2f}%")

    # --- Chart ---
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), **STYLE_KW,
                             gridspec_kw={"height_ratios": [2, 1]})

    # IC time series
    ax = axes[0]
    plot_dates = ic_raw.index[~ic_raw.isna()]
    window = 30  # rolling mean for clarity
    ax.plot(ic_raw.index, ic_raw.rolling(window, min_periods=5).mean(),
            color="#9e9e9e", linewidth=1.2, alpha=0.7, label=f"IC raw ({window}d MA)")
    ax.plot(ic_sec.index, ic_sec.rolling(window, min_periods=5).mean(),
            color="#1b5e20", linewidth=1.8, label=f"IC sector-demeaned ({window}d MA)")
    ax.plot(ic_sec_chain.index, ic_sec_chain.rolling(window, min_periods=5).mean(),
            color="#1565c0", linewidth=1.5, linestyle="--",
            label=f"IC sec+chain-demeaned ({window}d MA)")
    ax.axhline(0, color="black", linewidth=0.6)
    ax.set_ylabel("IC (Spearman)")
    ax.set_title("E6: group_neut demo — 5-day reversal alpha\n"
                 f"Variance between-sector: {alpha_var_between_pct:.1f}% of total alpha variance")
    ax.legend(loc="upper right")

    # Bar chart of mean IC and Sharpe
    ax2 = axes[1]
    variants = ["Raw", "Sector-\ndemeaned", "Sec+Chain-\ndemeaned"]
    means = [mean_raw, mean_sec, mean_sec_chain]
    sharpes = [sharpe_raw, sharpe_sec, sharpe_sec_chain]
    x = np.arange(3)
    c1, c2 = "#9e9e9e", "#1b5e20"
    b1 = ax2.bar(x - 0.2, means, 0.35, label="Mean IC", color=c1, alpha=0.85)
    b2 = ax2.bar(x + 0.2, [s / 10.0 for s in sharpes], 0.35,
                 label="IC Sharpe / 10", color=c2, alpha=0.85)
    ax2.set_xticks(x)
    ax2.set_xticklabels(variants, fontsize=10)
    ax2.set_ylabel("Mean IC  /  IC Sharpe ÷ 10")
    ax2.axhline(0, color="black", linewidth=0.6)
    ax2.legend(fontsize=9)

    for bar, val in zip(b1, means):
        ax2.text(bar.get_x() + bar.get_width() / 2.0, val + 0.0002,
                 f"{val:+.4f}", ha="center", va="bottom", fontsize=8)
    for bar, val in zip(b2, sharpes):
        ax2.text(bar.get_x() + bar.get_width() / 2.0, val / 10.0 + 0.0002,
                 f"{val:+.3f}", ha="center", va="bottom", fontsize=8)

    fig.autofmt_xdate()
    fig.savefig(CHARTS / "e6_groupneut_demo.png", **STYLE_KW)
    plt.close(fig)
    print(f"  chart -> {CHARTS / 'e6_groupneut_demo.png'}")

    return {
        "e6_mean_ic_raw": round(mean_raw, 6),
        "e6_mean_ic_sector_demeaned": round(mean_sec, 6),
        "e6_mean_ic_sec_chain_demeaned": round(mean_sec_chain, 6),
        "e6_ic_sharpe_raw": round(sharpe_raw, 4),
        "e6_ic_sharpe_sector_demeaned": round(sharpe_sec, 4),
        "e6_ic_sharpe_sec_chain_demeaned": round(sharpe_sec_chain, 4),
        "e6_alpha_variance_between_sector_pct": round(alpha_var_between_pct, 3),
    }


# ---------------------------------------------------------------------------
# Appendix: heatmap and ARI (regenerate from existing logic; keep filenames)
# ---------------------------------------------------------------------------

def appendix_heatmap_ari(corr_full: pd.DataFrame, snap: pd.DataFrame) -> None:
    """Regenerate heatmap.png and ari_vs_ward.png (appendix figures)."""
    print("[Appendix] Heatmap + ARI ...")

    assets = corr_full.index.intersection(snap.index)
    corr = corr_full.loc[assets, assets]

    # Heatmap sorted by sector
    sector = snap["sector_code"].reindex(assets)
    order = sector.sort_values().index
    corr_sorted = corr.loc[order, order]
    fig, ax = plt.subplots(figsize=(9, 8), **STYLE_KW)
    im = ax.imshow(corr_sorted.values, cmap="RdBu_r", vmin=-0.4, vmax=0.8, aspect="auto")
    ax.set_title("Pairwise correlation matrix sorted by sector (Appendix)")
    ax.set_xticks([])
    ax.set_yticks([])
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Cross-sectionally demeaned return correlation")
    sec_sorted = sector.loc[order]
    last = None
    for i, s in enumerate(sec_sorted):
        if s != last and last is not None:
            ax.axhline(i - 0.5, color="black", linewidth=0.4, alpha=0.7)
            ax.axvline(i - 0.5, color="black", linewidth=0.4, alpha=0.7)
        last = s
    fig.savefig(CHARTS / "heatmap.png", **STYLE_KW)
    plt.close(fig)

    # ARI vs Ward
    schemes = [
        ("class",      "class_code"),
        ("sector",     "sector_code"),
        ("sub_sector", "sub_sector_code"),
    ]
    corr_clean = corr.clip(-1, 1).fillna(0)
    dist = np.sqrt(np.clip(2 * (1 - corr_clean.values), 0, None))
    np.fill_diagonal(dist, 0)
    dist = (dist + dist.T) / 2
    condensed = squareform(dist, checks=False)
    Z = linkage(condensed, method="ward")

    ari_vals = []
    for key, col in schemes:
        lbl = snap[col].reindex(assets).astype(str).fillna("-1")
        k = int(snap[col].reindex(assets).nunique())
        if k < 2:
            continue
        ward_lbl = fcluster(Z, t=k, criterion="maxclust")
        ari = float(adjusted_rand_score(lbl, ward_lbl))
        ari_vals.append((key, k, ari))

    fig, ax = plt.subplots(figsize=(7, 4.5), **STYLE_KW)
    names_a = [r[0] for r in ari_vals]
    vals_a  = [r[2] for r in ari_vals]
    ax.bar(names_a, vals_a, color="#1565c0")
    ax.set_ylabel("Adjusted Rand Index vs Ward (1-corr)")
    ax.set_title("Agreement with unsupervised clustering (Appendix)")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylim(-0.05, max(0.5, max(vals_a) * 1.3) if vals_a else 0.5)
    fig.savefig(CHARTS / "ari_vs_ward.png", **STYLE_KW)
    plt.close(fig)
    print(f"  appendix charts written")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    t0 = time.time()

    if not RETURNS_PATH.exists():
        print(f"[ERROR] Missing: {RETURNS_PATH}", file=sys.stderr)
        return 1

    CHARTS.mkdir(parents=True, exist_ok=True)
    NUMBERS_PATH.parent.mkdir(parents=True, exist_ok=True)

    # -- Load data
    corr_full, snap, ss_names, sec_names, cls_names, returns_raw, demeaned = load_data()

    numbers: dict[str, Any] = {}

    # -- E1
    e1 = e1_within_between(corr_full, snap, demeaned, sec_names, cls_names)
    numbers.update(e1)
    t1 = time.time()
    print(f"  [timing] E1 done in {t1 - t0:.1f}s")

    # -- E2
    e2 = e2_per_sub_sector(corr_full, snap, ss_names)
    numbers.update(e2)
    t2 = time.time()
    print(f"  [timing] E2 done in {t2 - t1:.1f}s")

    # -- E3
    e3 = e3_multiple_testing(e1, e2)
    numbers.update(e3)

    # -- E4
    e4 = e4_rolling_stability(demeaned, snap)
    numbers.update(e4)
    t4 = time.time()
    print(f"  [timing] E4 done in {t4 - t2:.1f}s")

    # -- E5
    e5 = e5_baseline_comparison(corr_full, snap)
    numbers.update(e5)
    t5 = time.time()
    print(f"  [timing] E5 done in {t5 - t4:.1f}s")

    # -- E6
    e6 = e6_groupneut_demo(returns_raw, snap)
    numbers.update(e6)
    t6 = time.time()
    print(f"  [timing] E6 done in {t6 - t5:.1f}s")

    # -- Appendix
    appendix_heatmap_ari(corr_full, snap)

    # -- Write numbers.json
    NUMBERS_PATH.write_text(json.dumps(numbers, indent=2, default=str), encoding="utf-8")
    print(f"\n  wrote {NUMBERS_PATH}")

    elapsed = time.time() - t0
    print(f"\n[DONE] Total runtime: {elapsed:.1f}s ({elapsed / 60:.1f} min)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
