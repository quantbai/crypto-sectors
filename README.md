# crypto-sectors

> The open GICS for crypto — hierarchical sector taxonomy, validated against daily returns.

[![CI](https://github.com/quantbai/crypto-sectors/actions/workflows/ci.yml/badge.svg)](https://github.com/quantbai/crypto-sectors/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](LICENSE-data)

A hierarchical industry classification standard for digital assets — aligned with [MSCI Datonomy (Nov 2022)](https://www.msci.com/our-solutions/indexes/datonomy), with community-maintained extensions. Designed for cross-sectional risk decomposition, sector-neutral portfolio construction, and peer-group analysis.

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
# Cross-sectional demean within sector — a standard alpha-research operation
alpha_demeaned = alpha.sub(alpha.groupby(sector.loc[date], axis=1).transform("mean"))
```

## Coverage

- **Universe**: 158 actively classified digital assets
- **Hierarchy**: 4 classes → 14 sectors → ~35 sub-sectors (Datonomy-aligned + community extensions)
- **Orthogonal tag**: `chain_ecosystem` (BTC, ETH, SOL, BNB, …)
- **Update cadence**: quarterly snapshot tags (`v2026.Q2`, `v2026.Q3`, …), continuous PR review

## Validation in one sentence

> Same-sector daily returns co-move significantly more than cross-sector returns (bootstrap-CI spread well above zero), and the classification recovers the same cluster structure that an unsupervised Ward-linkage clustering of correlations would find. See [validation.md](validation.md).

## Why this exists

| Existing source | Limitation |
|---|---|
| **MSCI Datonomy** | Methodology public, asset mappings paywalled |
| **CoinGecko / CMC categories** | Marketing tags — not mutually exclusive, no methodology, no validation |
| **Internal fund taxonomies** | Each fund reinvents the wheel; nothing comparable |

This repo: open methodology, open mappings, empirically validated, community-curated.

## Contribute

Add a new token, propose a reclassification, or open a sub-sector discussion — see [CONTRIBUTING.md](CONTRIBUTING.md). Most PRs are one line in `classification/snapshot.csv` plus a short `decisions/<symbol>.md`.

## License

Code (`scripts/`) — MIT. Classification data (`taxonomy.yaml`, `classification/`, `decisions/`) — [CC BY 4.0](LICENSE-data). Attribute as:

> crypto-sectors contributors (2026). _crypto-sectors: an open industry classification standard for digital assets._ https://github.com/quantbai/crypto-sectors
