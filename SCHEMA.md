# Schema Reference

> Version 1.0.0-RC2 · crypto-sectors

This document is the authoritative dtype contract for every field published by this repository. Parquet is the canonical format for dtype purposes; CSV is a presentation-only convenience and does not preserve nullable integer semantics.

---

## Canonical vs presentation formats

| Format | Path | Purpose |
|---|---|---|
| **Parquet** (canonical) | `classification/wide/*.parquet`, `classification/long/panel.parquet` | Machine consumption, dtype-correct, nullable Int64 preserved |
| CSV (presentation only) | `classification/wide/*.csv`, `classification/long/panel.csv`, `classification/snapshot.csv` | Human reading, GitHub preview. Integer codes written without `.0` suffix. Do not use CSV as dtype reference. |

Downstream consumers who need dtype guarantees must read from parquet. If you read from CSV, cast explicitly:

```python
snap = pd.read_csv("classification/snapshot.csv")
for col in ["class_code", "sector_code", "sub_sector_code"]:
    snap[col] = snap[col].astype("Int64")
snap["effective_from"] = pd.to_datetime(snap["effective_from"]).dt.date
```

---

## Field definitions

### `classification/snapshot.csv` (and long panel)

| Field | dtype (parquet) | Nullable | Notes |
|---|---|---|---|
| `asset_id` | `string` | No | Stable identifier; lowercase, hyphen-separated (e.g. `terra-luna-classic`). Never changes across rebrands. |
| `symbol` | `string` | No | Current canonical trading symbol; uppercase alphanumeric. May change on rebrand. |
| `name` | `string` | No | Human-readable display name. |
| `class_code` | `Int64` | No | 2-digit class code. One of: 10, 20, 30, 40. |
| `sector_code` | `Int64` | No | 4-digit sector code. Must roll up to `class_code`. |
| `sub_sector_code` | `Int64` | No | 6-digit sub-sector code. Must roll up to `sector_code`. |
| `chain_ecosystem` | `string` | No | Dominant chain tag. Enumerated in `taxonomy.yaml` under `tags.chain_ecosystem.values`. **Usage flag: `FILTER_ONLY`.** This field is a categorical universe-gate / risk-decomposition tag. It is **not** a numeric alpha input. Do not feed it as a direct factor into IC-style alpha expressions; use it for `group_neut` or universe filtering only. |
| `effective_from` | `date` | No | Date from which this classification row applies. All v1.0 rows = `2024-05-23` (min date in `data/daily_returns.parquet`). Null is not permitted; a missing value indicates a data pipeline error. |

### `classification/wide/<field>.parquet`

One file per hierarchical field (`class_code`, `sector_code`, `sub_sector_code`, `chain_ecosystem`).

| Dimension | dtype | Notes |
|---|---|---|
| Index (rows) | `datetime64[ns]` | Daily dates. |
| Columns | `string` | `asset_id` values. |
| Cell values (`class_code`, `sector_code`, `sub_sector_code`) | `Int64` | See Int64 warning below. |
| Cell values (`chain_ecosystem`) | `string` | Ecosystem tag string. |

**NaN semantics in wide matrices**: Cells in `classification/wide/*.parquet` may be `<NA>` (pandas Int64 missing) for two reasons:

1. **Pre-effective-from**: `date < effective_from` of the asset's currently active row. The asset is not yet classified under this snapshot's schema.
2. **No returns data**: the asset exists in `snapshot.csv` but `data/daily_returns.parquet` has no observation for that date (asset not yet listed on the returns provider's universe). This produces NaN even when `date >= effective_from`. For example, on 2025-01-15 the wide matrix has 39 NaN sector cells from assets whose `effective_from` is 2024-05-23 but whose returns panel coverage began later.

Both are legitimate NaN; neither indicates a classification missing-data error. Downstream consumers should `.dropna()` or impute upstream of `group_neut` operations.

---

## Int64 numpy-safety warning

`Int64` is pandas' nullable integer type. It is **not** numpy-safe.

**Calling `.values` or `np.array()` on an `Int64` column returns `object` dtype with `pd.NA` values, not `int64`.** This silently breaks numpy and numba operations:

```python
# WRONG — returns object array, breaks numpy math
codes = sector_wide["btc"].values          # dtype: object

# WRONG — returns object array
import numpy as np
codes = np.array(sector_wide["btc"])       # dtype: object
```

To use sector codes in numpy / numba operations, escape via:

```python
# CORRECT — drops NaN rows first, then casts
codes = series.dropna().astype("int64")    # dtype: int64

# Or for a full column where you know NaN is absent:
codes = series.astype("int64")             # raises if NaN present — catch it
```

In wide matrices, NaN cells (pre-`effective_from`) will cause `.dropna()` to drop rows. This is intentional when constructing a cross-sectional slice at a specific date after all assets are classified.

---

## Null policy summary

| Field | Null permitted | Null meaning |
|---|---|---|
| `asset_id` | No | — |
| `symbol` | No | — |
| `name` | No | — |
| `class_code` | No | — |
| `sector_code` | No | — |
| `sub_sector_code` | No | — |
| `chain_ecosystem` | No | — |
| `effective_from` | **No** | Null = pipeline error; fail loudly |
| Wide matrix cell (`class_code`, `sector_code`, `sub_sector_code`) | Yes (as `pd.NA`) | (1) Pre-classification: `date < effective_from`; or (2) asset has no returns data for that date |
| Wide matrix cell (`chain_ecosystem`) | Yes (as `pd.NA`) | Same two causes as numeric code cells |

---

## Referential integrity

`validate_schema.py` asserts at CI time:

- No duplicate `asset_id` in snapshot
- No duplicate `symbol` in snapshot
- All `class_code`, `sector_code`, `sub_sector_code` values exist in `taxonomy.yaml`
- Hierarchical rollup is consistent (`sub_sector_code` → `sector_code` → `class_code`)
- All `chain_ecosystem` values are enumerated in `taxonomy.yaml`
- `asset_id` format: lowercase, hyphen-separated
- `symbol` format: uppercase alphanumeric
- `effective_from` present, parseable as date, no nulls
- No duplicate `(asset_id, effective_from)` pairs
