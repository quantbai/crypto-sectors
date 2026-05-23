"""
build_matrices.py
=================

Builds the published classification artifacts from two inputs:

  1. classification/snapshot.csv      ← canonical, human-edited
  2. data/daily_returns.parquet       ← returns universe (provides date range)

Outputs (regenerated, idempotent):

  classification/wide/{class_code,sector_code,sub_sector_code,chain_ecosystem}.csv
                     .parquet                                    ← (date × asset_id)
  classification/long/panel.csv .parquet                          ← (date, asset_id, ...codes)

Columns in wide matrices are asset_ids (not symbols) to avoid ticker-collision
bugs across asset migrations (e.g. LUNA referred to terra-luna-original
pre-2022-05 and terra-luna-2 thereafter).

Run:
    python scripts/build_matrices.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "classification" / "snapshot.csv"
RETURNS = ROOT / "data" / "daily_returns.parquet"
WIDE_DIR = ROOT / "classification" / "wide"
LONG_DIR = ROOT / "classification" / "long"

FIELDS = ["class_code", "sector_code", "sub_sector_code", "chain_ecosystem"]


def main() -> int:
    if not SNAPSHOT.exists():
        print(f"[ERROR] {SNAPSHOT} not found.", file=sys.stderr)
        return 1
    if not RETURNS.exists():
        print(f"[ERROR] {RETURNS} not found.", file=sys.stderr)
        print("        Run scripts/pull_returns.py first.", file=sys.stderr)
        return 1

    snap = pd.read_csv(SNAPSHOT)
    returns = pd.read_parquet(RETURNS)
    returns.index = pd.to_datetime(returns.index)
    dates = [ts.date() for ts in returns.index]

    print(f"snapshot:    {len(snap)} assets")
    print(f"returns:     {returns.shape[0]} days × {returns.shape[1]} assets "
          f"({dates[0]} → {dates[-1]})")

    # Asset_id is canonical key. Map snapshot symbols to returns columns.
    # The current returns parquet keys by ticker; we translate ticker → asset_id.
    sym_to_aid = dict(zip(snap.symbol, snap.asset_id))
    asset_ids_in_returns: list[str | None] = [sym_to_aid.get(s) for s in returns.columns]
    keep_mask = [aid is not None for aid in asset_ids_in_returns]
    n_dropped = sum(1 for k in keep_mask if not k)
    if n_dropped:
        dropped = [s for s, k in zip(returns.columns, keep_mask) if not k]
        print(f"[WARN] {n_dropped} returns columns have no snapshot match, dropped: {dropped[:5]}...")
    asset_ids: list[str] = [aid for aid in asset_ids_in_returns if aid is not None]
    returns = returns.loc[:, keep_mask]
    returns.columns = pd.Index(asset_ids)

    snap_idx = snap.set_index("asset_id")

    WIDE_DIR.mkdir(parents=True, exist_ok=True)
    LONG_DIR.mkdir(parents=True, exist_ok=True)

    # --- WIDE matrices ---
    for field in FIELDS:
        mat = pd.DataFrame(
            index=pd.Index(dates, name="date"),
            columns=pd.Index(asset_ids),
            dtype=object,
        )
        for aid in asset_ids:
            if aid not in snap_idx.index:
                continue
            val = snap_idx.at[aid, field]
            if pd.isna(val) or val == "":
                continue
            mat[aid] = val
        # NaN where returns are NaN (asset not yet listed / delisted)
        existence = returns.notna()
        existence.index = mat.index
        mat = mat.where(existence.values, other=pd.NA)

        # Numeric dtypes for code columns
        if field.endswith("_code"):
            mat = mat.apply(pd.to_numeric, errors="coerce").astype("Int64")

        out_pq = WIDE_DIR / f"{field}.parquet"
        out_csv = WIDE_DIR / f"{field}.csv"
        mat.to_parquet(out_pq)
        mat_csv = mat.copy()
        mat_csv.index = pd.Index([d.isoformat() for d in dates], name="date")
        mat_csv.to_csv(out_csv)
        n_filled = int(mat.notna().sum().sum())
        n_total = mat.shape[0] * mat.shape[1]
        print(f"  wide/{field:20s}  shape={mat.shape}  "
              f"filled={n_filled}/{n_total} ({100*n_filled/n_total:.1f}%)")

    # --- LONG panel ---
    panel_long = []
    for aid in asset_ids:
        if aid not in snap_idx.index:
            continue
        row = snap_idx.loc[aid]
        existence = returns[aid].notna()
        for d in existence.index[existence]:
            panel_long.append({
                "date": d.date().isoformat(),
                "asset_id": aid,
                "symbol": row.get("symbol", ""),
                "class_code": row["class_code"],
                "sector_code": row["sector_code"],
                "sub_sector_code": row["sub_sector_code"],
                "chain_ecosystem": row["chain_ecosystem"],
            })
    long_df = pd.DataFrame(panel_long)
    long_df.to_csv(LONG_DIR / "panel.csv", index=False)
    long_df.to_parquet(LONG_DIR / "panel.parquet", index=False)
    print(f"  long/panel             rows={len(long_df):,}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
