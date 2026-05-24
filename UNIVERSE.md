# Universe Definition

> Version 1.0.0-RC2 · crypto-sectors

---

## 1. Coverage universe vs investable universe

This repository defines a **coverage universe**: the set of assets that are actively classified under this taxonomy. It does not define an investable universe.

- **Coverage universe** (this file): 158 assets with an assigned classification in `classification/snapshot.csv`. Inclusion is based on economic significance and data availability as defined in §2.
- **Investable universe** (downstream, not this repo): the subset of the coverage universe that a specific strategy can actually trade, after applying per-strategy filters for mcap tier, ADV, venue listing, regulatory status, and custody constraints. Consumers apply their own investable filters to our coverage.

Metrics in `validation.md` are computed on the 156 assets that have returns data (see §5 for the 2-asset discrepancy).

---

## 2. Hard inclusion criteria

An asset is eligible for the coverage universe if it satisfies all of the following at the time of snapshot:

| Criterion | Threshold | Rationale |
|---|---|---|
| **Free-float market cap** | >= $25M USD at snapshot date | Below this floor, price impact from index-replication flows dominates organic price discovery; intra-group correlations become unreliable. |
| **30-day average daily volume (ADV)** | >= $500K USD across tier-1 venues | Ensures sufficient price history quality; below this, bid-ask spread noise degrades daily return reliability. |
| **Returns history** | >= 30 calendar days of non-null daily returns in `data/daily_returns.parquet` | Minimum window to compute pairwise correlations for sub-sector validation. |
| **Venue presence** | Listed on >= 1 tier-1 venue (Binance, Coinbase, OKX, Kraken, Bybit) | Ensures data availability and basic liquidity. |
| **Excludes stablecoins in directional universe** | Assets in class 40 (Stablecoins sub-sectors 401010–401030) are classified but not included in directional returns analysis | Stablecoins are in the taxonomy for completeness but are filter targets, not group_neut targets. |

**v1.0 grandfathered exceptions to the 90-day history rule**: The following assets are included in the v1.0 snapshot despite not meeting the 30-day history floor (raised to 90-day for v1.1 mechanical enforcement). They are admitted on strategic grounds — each is an ecosystem token with significant market interest or an audit-trail anchor — and will be subject to automated threshold enforcement from v1.1 onward. v1.1 onward will enforce mechanically via `validate_schema.py` before any new asset is added to snapshot.

| asset_id | symbol | valid_days | criterion_failed |
|---|---|---|---|
| `terra-luna-classic` | LUNC | 0 | absent from returns panel |
| `genius` | GENIUS | 0 | history < 90 days |
| `terra-luna-2` | LUNA | 0 | absent from returns panel |
| `bill` | BILL | 18 | history < 90 days |
| `edge` | EDGE | 52 | history < 90 days |
| `xaut` | XAUT | 57 | history < 90 days |
| `cfg` | CFG | 67 | history < 90 days |
| `night` | NIGHT | 72 | history < 90 days |

Assets with `absent from returns panel` show as all-NaN columns in the wide matrix (see §5). Assets with `history < 90 days` have partial returns coverage; their NaN cells precede their first observed return date.

---

## 3. Exclusions

The following asset categories are explicitly excluded from the active classification universe even if they technically meet the mcap / ADV floors:

| Category | Example assets | Reason |
|---|---|---|
| **Fiat-backed stablecoins** | USDT, USDC, BUSD | Zero directional exposure; intra-group correlation undefined. Classified in 401010 for taxonomy completeness but omitted from active directional universe. |
| **Algorithmic stablecoins** | FRAX, TUSD | Same rationale as fiat-backed; peg-break events create extreme outlier returns that distort group statistics. |
| **Wrapped / bridged mirrors of included assets** | WBTC, WETH, cbBTC | Price is mechanically derived from the underlying; including both double-counts the underlying's sector exposure. The underlying is the classified asset. |
| **Native L2 mirrors of included L1s** | No current examples; reserved | Where a rollup has its own native token that is 1:1 backed by the L1 gas token, classify the L1 only. |
| **Tokenized equity or commodity receipts** | TSLA on-chain, tokenized gold via CEX | Classified in 402010 (Asset-Backed Tokens) if present, but excluded from directional demean universe because they are derivatives of off-chain assets. |

---

## 4. Candidate graduation rule

An asset moves from "candidate" (community-proposed but not yet active) to "active" in the snapshot through this process:

1. A community PR is opened adding one row to `classification/snapshot.csv` and one `decisions/<symbol>.md` file.
2. The PR must demonstrate that all four hard criteria in §2 are met at the time of the PR submission, with verifiable sources (e.g. CoinGecko mcap link, exchange volume screenshot, or API pull dated within 7 days).
3. A maintainer reviews the classification rationale in `decisions/<symbol>.md` against the taxonomy definitions.
4. If approved, the asset is merged into `snapshot.csv` and will appear in the next quarterly tag.
5. Off-cycle additions are permitted for fraud / de-peg / chain-migration events that require emergency reclassification of an existing asset.

---

## 5. Validation data discrepancy: n=156 vs snapshot n=158

`validation.md` reports statistics for n=156 assets. Two assets in `snapshot.csv` have no returns data in `data/daily_returns.parquet`:

| asset_id | symbol | Reason for no returns data |
|---|---|---|
| `terra-luna-classic` | LUNC | Returns data for the post-collapse LUNC token (renamed from LUNA after May 2022) was not available in the source returns panel. The asset remains in snapshot for symbol-history audit purposes (see `decisions/luna-symbol-history.md`) and to anchor the `asset_id` namespace. |
| `terra-luna-2` | LUNA | The new Terra chain launched post-collapse and pre-dates this snapshot, but its returns series was not included in the source panel. Same audit-trail rationale. |

These assets are classified in snapshot but will show as all-NaN columns in the wide matrix. Downstream consumers should handle them via `dropna(how="all", axis=1)` if they wish to exclude no-return assets from analysis.
