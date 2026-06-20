# crypto-sectors

> A single flat `sector` field for the 232-coin OKX perpetual universe, empirically validated for cross-sectional group-neutralization (`group_neut`).

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](LICENSE-data)

---

## What this is

**crypto-sectors** publishes one thing: a single flat `sector` label for every coin in the
232-coin OKX USDT-margined perpetual universe, validated for use as a group-neutralization
(`group_neut`) input in cross-sectional crypto factor research.

Universe: 232 crypto-native coins. Identity anchored by `cg_id` (CoinGecko slug) +
`okx_instid` to prevent ticker-collision mis-resolution. Daily log-returns span
2019-11-27 to 2026-06-13 (2391 rows).

This is **not** a covariance model or a risk model. It is a validated classification — an
input to an exposure matrix. Do not use sector labels as regression variables or factor
returns directly.

---

## The 15-label sector field

One layer, no hierarchy, no numeric codes. Each label is defined economics-first in
`taxonomy.yaml` with ordered precedence rules.

### FACTOR sectors — within-group demean removes a real shared return factor

**STRONG** (mean intra-group market-residual pairwise correlation, 10k-perm):

| Sector | Mean residual corr |
|---|---|
| `privacy` | +0.55 |
| `captive_franchise` | +0.30 |
| `value_transfer` | +0.23 |
| `compute_storage` | +0.18 |
| `meme` | +0.10 |

**WEAK but significant:**

| Sector | Mean residual corr |
|---|---|
| `eth_scaling` | +0.04 |
| `metaverse_gaming` | +0.04 |
| `interoperability` | +0.03 |

**MARGINAL** — significant only because large n tightens the permutation null; cohesion
is mostly market beta. Treat with caution:

| Sector | Mean residual corr |
|---|---|
| `smart_contract_platform` | +0.013 |
| `information_technology` | +0.011 |

### RESIDUAL sectors — intra-group correlation indistinguishable from null

Demean within these groups is approximately a no-op. They are **pooled into OTHER** in
the production `group_neut` kernel. Kept as organizational labels; candidates for
sub-division once each sub-leaf has >= 3 live members.

| Sector | Mean residual corr |
|---|---|
| `defi` | +0.003 |
| `ai_infrastructure` | -0.002 |
| `oracles_data` | +0.008 |
| `media_content` | +0.005 |
| `OTHER` | (catch-all) |

Full per-label statistics: `validation/sector_okx/cohesion_sector.csv`.

---

## Validation — 10,000-perm, production OTHER-collapse kernel

Method: per-day cross-sectional variance reduction (VR) vs a size-preserving label-shuffle
null, averaged over days with >= `min_assets` valid coins.

| Slice | n coins | min_assets | VR | Null mean | Excess | p |
|---|---|---|---|---|---|---|
| ALL | 232 | 30 | 12.91% | 8.22% | +4.69 pp | 0.0001 |
| TOP30 | top 30 | 20 | 22.78% | 16.03% | +6.75 pp | 0.0008 |
| TOP50 | top 50 | 30 | 17.97% | 11.50% | +6.48 pp | 0.0001 |
| TOP100 | top 100 | 40 | 17.46% | 11.75% | +5.71 pp | 0.0001 |

Full run log: `validation/sector_okx/run_10k.log`. Summary: `validation/sector_okx/REPORT.md`.

---

## Production OTHER-collapse kernel

This is the conservative/honest kernel — what `group_neut` does and what the VR numbers
above measure. A naive "demean within every label" overstates VR.

**Per day:**
1. Identify FACTOR sectors with >= 3 live members on that date.
2. Demean returns within each such group.
3. Pool RESIDUAL-labelled coins **and** any FACTOR group with < 3 live members on that
   date into a single `OTHER` bucket.
4. Demean the `OTHER` pool (market-neutralize the remainder).

---

## Honesty notes

- **`ai_infrastructure` and `oracles_data`** are new carve-outs that are RESIDUAL — they
  do not pass cohesion alone. Kept as organizational labels, pooled into `OTHER` in
  `group_neut`. Candidates for sub-division (e.g., `defi` -> dex/lending/lsd/rwa/perps;
  `ai_infrastructure` -> gpu-compute/agents/data) once each sub-leaf has >= 3 live members.

- **Big buckets** (`smart_contract_platform`, `information_technology`, `defi`) are mostly
  market beta. Their statistical significance comes from large n tightening the null, not
  from strong cohesion.

- **NOT A RISK MODEL.** This is a validated classification — an input to a risk model's
  exposure matrix. It is not a covariance model or factor risk model.

- **Deployment gate.** Validated for research and group-neutralization. Alpha-capital
  deployment is paper-trading-gated.

---

## Repository contents

| Path | Description |
|---|---|
| `classification/sector.csv` | Committed source of truth. Columns: `symbol`, `sector`, `role`, `cg_id`, `okx_instid`, `audit_from`, `prev_label`, `note`. 232 rows. |
| `classification/sector.parquet` | Parquet mirror (derived by `scripts/build_sector_field.py`). |
| `classification/sector_panel.parquet` | PIT (date × symbol) label matrix, pandas `StringDtype`, `<NA>` before listing. The direct `group_neut` input. |
| `classification/sector_roles.json` | `label -> {role, n, mean_resid_corr, cohesion_p}` |
| `classification/universe_tiers.json` | TOP10/20/30/50/100 membership lists. |
| `data/returns.parquet` | 232-symbol daily log-returns. |
| `taxonomy.yaml` | Flat sector label definitions (economics-first), precedence/boundary rules, FACTOR/RESIDUAL governance note. |
| `decisions/` | Per-coin economic rationale. `decisions/sector-field.md` is the master memo; `decisions/sector-field-okx-2026-06.md` is the audit record. |
| `research/` | 128 per-coin economic-rationale notes. |
| `validation/sector_okx/` | `varred_sector.json`, `cohesion_sector.csv`, `run_10k.log`, `REPORT.md`. |
| `scripts/` | `build_sector_field.py`, `validate_sector_okx.py`, `validate_schema.py`, `README.md`. |
| `.github/workflows/ci.yml` | CI: build + schema-validate + smoke-validate on published files. |

---

## Quick start

```python
import pandas as pd

# Load the PIT label panel and returns
panel   = pd.read_parquet("classification/sector_panel.parquet")   # date x symbol, StringDtype
returns = pd.read_parquet("data/returns.parquet")                   # date x symbol, float64

# Align
common_dates  = panel.index.intersection(returns.index)
common_assets = panel.columns.intersection(returns.columns)
panel   = panel.loc[common_dates, common_assets]
returns = returns.loc[common_dates, common_assets]


def group_neut_day(ret: pd.Series, lbl: pd.Series) -> pd.Series:
    """
    Production OTHER-collapse group_neut for one cross-section.

    - FACTOR groups with >= 3 live members: demean within group.
    - RESIDUAL labels + any FACTOR group with < 3 live members:
      pooled into OTHER, then market-neutralized.
    """
    # Drop assets missing either return or label
    valid = ret.dropna().index.intersection(lbl.dropna().index)
    r = ret[valid].copy()
    g = lbl[valid].copy()

    # Load FACTOR labels (from classification/sector_roles.json in practice)
    FACTOR_LABELS = {
        "privacy", "captive_franchise", "value_transfer", "compute_storage", "meme",
        "eth_scaling", "metaverse_gaming", "interoperability",
        "smart_contract_platform", "information_technology",
    }

    # Collapse RESIDUAL labels and under-populated FACTOR groups into OTHER
    counts = g.value_counts()
    def collapse(label):
        if label not in FACTOR_LABELS:
            return "OTHER"
        if counts.get(label, 0) < 3:
            return "OTHER"
        return label

    g = g.map(collapse)

    # Within-group demean
    group_means = r.groupby(g).mean()
    return r - g.map(group_means)


# Apply to a single date
date = "2025-01-15"
neutralized = group_neut_day(returns.loc[date], panel.loc[date])
```

---

## Reproduce

```bash
# Derive parquet + panel + roles from sector.csv (committed source of truth)
python scripts/build_sector_field.py

# Full 10,000-perm validation (~1.5 h)
python scripts/validate_sector_okx.py --n-perm 10000

# Smoke test (fast)
python scripts/validate_sector_okx.py --n-perm 200

# Referential integrity check
python scripts/validate_schema.py
```

---

## Status

Single flat `sector` field on the 232-coin OKX perpetual universe. Pre-release.

Validated for research and group-neutralization. Alpha-capital deployment is
paper-trading-gated.

---

## License

Code (`scripts/`) — [MIT](LICENSE).
Data (`taxonomy.yaml`, `classification/`, `decisions/`) — [CC BY 4.0](LICENSE-data).

Attribution:

> crypto-sectors contributors (2026). *crypto-sectors: a validated sector classification for the OKX crypto perpetual universe.* https://github.com/quantbai/crypto-sectors
