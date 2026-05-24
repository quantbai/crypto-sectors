# crypto-sectors

> Open hierarchical industry classification for digital assets, validated against daily returns.

[![CI](https://github.com/quantbai/crypto-sectors/actions/workflows/ci.yml/badge.svg)](https://github.com/quantbai/crypto-sectors/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](LICENSE-data)

A community-maintained, hierarchical industry classification for digital assets. Designed for cross-sectional risk decomposition, sector-neutral portfolio construction, and peer-group analysis. The hierarchy is informed by established institutional classification methodologies — see [methodology.md](methodology.md) for citations.

---

## What you get

| File | Description |
|---|---|
| [`taxonomy.yaml`](taxonomy.yaml) | Source of truth — class / sector / sub-sector definitions and codes |
| [`classification/snapshot.csv`](classification/snapshot.csv) | Current classification of every covered asset |
| [`classification/wide/<field>.parquet`](classification/wide/) | (date × asset) matrices, drop-in for `group_neut` style operations |
| [`classification/long/panel.parquet`](classification/long/) | (date, asset_id, codes) long form for SQL warehouses |
| [`decisions/`](decisions/) | One file per non-trivial classification decision — the audit trail |
| [`methodology.md`](methodology.md) | The rulebook — how classifications are made |
| [`validation.md`](validation.md) | Empirical evidence the classification co-moves on daily returns |
| [`UNIVERSE.md`](UNIVERSE.md) | Coverage universe — selection criteria, exclusions, and graduation rules |
| [`GOVERNANCE.md`](GOVERNANCE.md) | Maintainer council, PR merge thresholds, conflict-of-interest policy, appeals |
| [`SCHEMA.md`](SCHEMA.md) | Dtype contract for all published fields; Int64 numpy-safety warning |
| [`CHANGELOG.md`](CHANGELOG.md) | Version history; v1.1 reclassifications.csv forward contract |

## Quick start

```python
import pandas as pd

# Wide matrix: dates × asset_ids, cells = integer sector code
sector = pd.read_parquet(
    "https://raw.githubusercontent.com/quantbai/crypto-sectors/main/classification/wide/sector_code.parquet"
)

# Or just the latest snapshot for human reading
snapshot = pd.read_csv(
    "https://raw.githubusercontent.com/quantbai/crypto-sectors/main/classification/snapshot.csv"
)
print(snapshot.head())
```

For a sector-neutralization example:

```python
import datetime

# date must be a datetime.date (not pd.Timestamp) to index the wide matrix
date = datetime.date(2025, 1, 15)

# Note: cells before effective_from (2024-05-23) are NaN — a sane backtest
# starts on or after that date.
sector = pd.read_parquet(
    "https://raw.githubusercontent.com/quantbai/crypto-sectors/main/classification/wide/sector_code.parquet"
)

# Align sector codes to alpha column order; prevents silent NaN from column mismatch
sector_row = sector.loc[pd.Timestamp(date)].reindex(alpha.columns)

# Cross-sectional demean within sector — a standard alpha-research operation
# (.T.groupby().T replaces the deprecated groupby(axis=1))
# Note: assets with NA sector_row (e.g. pre-effective_from, no-returns) are
# silently set to NaN in alpha_demeaned. Filter or impute upstream.
alpha_demeaned = alpha.sub(alpha.T.groupby(sector_row).transform("mean").T)
```

## Coverage

- **Universe**: 158 actively classified digital assets. See [UNIVERSE.md](UNIVERSE.md) for selection criteria and exclusions.
- **Hierarchy**: 4 classes → 14 sectors → ~35 sub-sectors (community-maintained, with extensions in the 90–99 slot of each sector)
- **Orthogonal tag**: `chain_ecosystem` (BTC, ETH, SOL, BNB, …) — categorical `FILTER_ONLY` tag; see [SCHEMA.md](SCHEMA.md) for usage guidance. Do not use as a direct numeric alpha factor.
- **Update cadence**: quarterly snapshot tags (`v2026.Q2`, `v2026.Q3`, …), continuous PR review

## Validation in one sentence

> Same-sector daily returns co-move significantly more than cross-sector returns (bootstrap-CI spread well above zero), and the classification recovers the same cluster structure that an unsupervised Ward-linkage clustering of correlations would find. See [validation.md](validation.md).

## Why this exists

| Existing source | Limitation |
|---|---|
| Commercial institutional classifications | Methodology often public, but asset-level mappings are paid products |
| CoinGecko / CMC categories | Marketing tags — not mutually exclusive, no formal methodology, no empirical validation |
| Internal fund taxonomies | Each fund reinvents the wheel; nothing comparable across teams |

This repository: open methodology, open mappings, empirically validated, community-curated.

## Contribute

Add a new token, propose a reclassification, or open a sub-sector discussion — see [CONTRIBUTING.md](CONTRIBUTING.md). Most PRs are one line in `classification/snapshot.csv` plus a short `decisions/<symbol>.md`.

## License

Code (`scripts/`) — MIT. Classification data (`taxonomy.yaml`, `classification/`, `decisions/`) — [CC BY 4.0](LICENSE-data). Attribute as:

> crypto-sectors contributors (2026). _crypto-sectors: an open industry classification for digital assets._ https://github.com/quantbai/crypto-sectors

## Notice of non-affiliation

This is an independent open-source project. It is not affiliated with, endorsed by, or sponsored by MSCI Inc., S&P Global, FTSE Russell, Coin Metrics, Goldman Sachs, WorldQuant LLC, or any other commercial index, classification, or analytics provider. References to third-party methodologies in [methodology.md](methodology.md) are academic citations and do not imply any business relationship. All trademarks are the property of their respective owners.
