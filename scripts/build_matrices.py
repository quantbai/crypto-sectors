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

PIT semantics:
  For each (date, asset_id), the value used is from the snapshot row with the
  latest effective_from <= date.  For dates before every row's effective_from,
  the cell is NaN.  In v1.0 (one row per asset), this means all cells before
  2024-05-23 are NaN.

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


def _pit_lookup(snap_for_asset: pd.DataFrame, date) -> pd.Series | None:
    """Return the snapshot row active on `date` (effective_from <= date).

    `date` must be comparable to the effective_from column values (both
    datetime.date or both pd.Timestamp).  Returns None if no row qualifies.
    """
    candidates = snap_for_asset[snap_for_asset["effective_from"] <= date]
    if candidates.empty:
        return None
    return candidates.loc[candidates["effective_from"].idxmax()]


def main() -> int:
    if not SNAPSHOT.exists():
        print(f"[ERROR] {SNAPSHOT} not found.", file=sys.stderr)
        return 1
    if not RETURNS.exists():
        print(f"[ERROR] {RETURNS} not found.", file=sys.stderr)
        print("        Run scripts/pull_returns.py first.", file=sys.stderr)
        return 1

    snap = pd.read_csv(SNAPSHOT, parse_dates=["effective_from"])
    snap["effective_from"] = pd.to_datetime(snap["effective_from"]).dt.date

    returns = pd.read_parquet(RETURNS)
    returns.index = pd.to_datetime(returns.index)

    # B1 fix: use DatetimeIndex not plain list
    dates = pd.DatetimeIndex(returns.index)
    # For PIT lookup we compare date objects
    date_objects = [ts.date() for ts in dates]

    print(f"snapshot:    {len(snap)} assets")
    print(f"returns:     {returns.shape[0]} days x {returns.shape[1]} assets "
          f"({date_objects[0]} -> {date_objects[-1]})")

    # Asset_id is canonical key. Map snapshot symbols to returns columns.
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

    # Build per-asset group dict for fast PIT lookup
    # snap_by_aid: asset_id -> DataFrame of rows sorted by effective_from
    snap_by_aid: dict[str, pd.DataFrame] = {}
    for aid, grp in snap.groupby("asset_id"):
        snap_by_aid[aid] = grp.sort_values("effective_from")

    WIDE_DIR.mkdir(parents=True, exist_ok=True)
    LONG_DIR.mkdir(parents=True, exist_ok=True)

    # --- WIDE matrices ---
    for field in FIELDS:
        # Build date x asset_id matrix with PIT lookup
        mat = pd.DataFrame(
            pd.NA,
            index=dates,           # DatetimeIndex
            columns=pd.Index(asset_ids),
            dtype=object,
        )
        mat.index.name = "date"

        for aid in asset_ids:
            if aid not in snap_by_aid:
                continue
            aid_snap = snap_by_aid[aid]
            for i, d in enumerate(date_objects):
                pit_row = _pit_lookup(aid_snap, d)
                if pit_row is None:
                    continue
                val = pit_row[field]
                if pd.isna(val) or val == "":
                    continue
                mat.at[dates[i], aid] = val

        # NaN where returns are NaN (asset not yet listed / delisted)
        existence = returns.notna()
        existence.index = mat.index
        mat = mat.where(existence.values, other=pd.NA)

        # Numeric dtypes for code columns
        if field.endswith("_code"):
            mat = mat.apply(pd.to_numeric, errors="coerce").astype("Int64")

        out_pq = WIDE_DIR / f"{field}.parquet"
        out_csv = WIDE_DIR / f"{field}.csv"

        # Parquet: canonical — keeps DatetimeIndex + Int64
        mat.to_parquet(out_pq)

        # CSV: string-format dates, no .0 suffix on integer codes
        mat_csv = mat.copy()
        mat_csv.index = pd.Index([d.isoformat() for d in date_objects], name="date")
        mat_csv.to_csv(out_csv)

        n_filled = int(mat.notna().sum().sum())
        n_total = mat.shape[0] * mat.shape[1]
        print(f"  wide/{field:20s}  shape={mat.shape}  "
              f"filled={n_filled}/{n_total} ({100*n_filled/n_total:.1f}%)")

    # --- LONG panel (PIT lookup, same semantics as wide) ---
    panel_long = []
    for aid in asset_ids:
        if aid not in snap_by_aid:
            continue
        aid_snap = snap_by_aid[aid]
        existence = returns[aid].notna()
        for ts in existence.index[existence]:
            d = ts.date()
            pit_row = _pit_lookup(aid_snap, d)
            if pit_row is None:
                # date before first effective_from — no classification yet, omit
                continue
            panel_long.append({
                "date": d.isoformat(),
                "asset_id": aid,
                "symbol": pit_row.get("symbol", ""),
                "class_code": pit_row["class_code"],
                "sector_code": pit_row["sector_code"],
                "sub_sector_code": pit_row["sub_sector_code"],
                "chain_ecosystem": pit_row["chain_ecosystem"],
            })

    long_df = pd.DataFrame(panel_long)
    # Cast code columns to Int64 for dtype parity with wide matrices
    for col in ["class_code", "sector_code", "sub_sector_code"]:
        long_df[col] = pd.to_numeric(long_df[col], errors="coerce").astype("Int64")

    long_df.to_csv(LONG_DIR / "panel.csv", index=False)
    long_df.to_parquet(LONG_DIR / "panel.parquet", index=False)
    print(f"  long/panel             rows={len(long_df):,}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
