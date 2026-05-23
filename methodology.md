# Methodology

> Version 1.0.0 · Release date 2026-05-23

## 1. Purpose

A reference industry classification for digital assets, usable for:

1. **Cross-sectional sector neutralization** of alpha signals (`group_neut`).
2. **Risk attribution** — decomposing returns into sector, chain, and idiosyncratic components.
3. **Peer-group comparison** — fundamental and technical metrics are only meaningful relative to peers performing a similar economic function.
4. **Comparability with sell-side / institutional research** — codes are 1:1 compatible with MSCI Datonomy (Nov 2022) for the baseline 41 sub-sectors.

## 2. Design principles

| # | Principle | Why |
|---|-----------|-----|
| 1 | **Single-leaf assignment** within the hierarchy | An asset belonging to multiple groups is unusable for `group_neut`. We accept the cost: borderline assets are placed in their dominant economic function, with the rationale recorded in `decisions/`. |
| 2 | **Theory-driven, empirically validated** | The taxonomy starts from MSCI Datonomy's economic-function definitions. Sectors are not discovered from clustering — that would overfit. We then validate that same-sector returns co-move more than cross-sector returns. |
| 3 | **Orthogonal tags alongside the hierarchy** | Chain-ecosystem effects in crypto can rival sector effects. Forcing them into the hierarchy distorts the tree; treating them as a cross-cutting tag preserves both axes. |
| 4 | **Auditable per-asset decisions** | Every non-trivial classification has a markdown file in `decisions/` recording the rationale. Disputes become PRs with evidence. |

## 3. Hierarchy

Three levels, MSCI Datonomy-aligned:

```
Class (2-digit, 4 entries)            ── reporting & risk-regime boundary
  └── Sector (4-digit, 14 entries)    ── primary group-neutralization axis
        └── Sub-sector (6-digit)      ── attribution & fine-grained neutralization
```

### 3.1 Why three levels (and not two, or four)

The choice tracks the precedent set by [GICS](https://www.spglobal.com/spdji/en/landing/topic/gics/) and [ICB](https://www.ftserussell.com/data/industry-classification-benchmark-icb) for equities (both four-level systems with 5,000+ constituents), adjusted downward by one level because the digital-asset universe is roughly an order of magnitude smaller.

| Level count | Avg assets / leaf (at N=158) | Trade-off |
|---|---|---|
| 1 (sector only) | 11 | Loses the Currencies-vs-Smart-Contract-Platforms-vs-Stablecoin boundary; statistically forces stablecoins into the same demean bucket as L1 tokens. |
| 2 (class + sector) | sector: 11; class: 40 | Workable but loses application-level attribution (e.g., DEX vs Lending within DeFi). |
| **3 (class + sector + sub-sector)** | **sub: 3–5; sector: 11; class: 40** | **Sweet spot for current N.** Sub-sector statistically borderline; fallback chain (sub → sector → class) handles it. |
| 4 (add sub-industry) | sub-industry: 1–2 | Demean on n=1 is the asset itself. Not yet useful at this universe size. |

Each level serves a distinct downstream purpose: Class for stablecoin-vs-rest risk boundaries and UI navigation; Sector as the primary group-neutralization axis (empirically the strongest cohesion signal); Sub-sector for attribution and the largest-bucket niche neutralization (DEX, Lending, L2, LST).

### 3.2 Code structure

Six-digit codes follow `CCSSXX`:

- `CC` = class (2-digit)
- `SS` = sector-within-class (4-digit when concatenated as `CCSS`)
- `XX` = sub-sector-within-sector (6-digit when concatenated as `CCSSXX`)

Sub-sector codes ending `90`–`99` are community extensions beyond the Datonomy 2022 baseline. They are visually distinguishable (e.g., `301090` for Liquid Staking) and will not collide with future Datonomy revisions.

### 3.3 Orthogonal tags

| Tag | Cardinality | Why orthogonal to hierarchy |
|---|---|---|
| `chain_ecosystem` | ~10 | A lending protocol on Solana co-moves with other Solana assets more than with lending protocols on other chains. Sector and chain are both real, both significant; neither subsumes the other. |

Tags can be added in future versions for further orthogonal axes (token economic model, settlement-layer dependency, regulatory regime) but each addition requires evidence that the new axis captures meaningful variance not absorbed by hierarchy or existing tags.

## 4. Classification process

### 4.1 New asset

1. **Read** whitepaper, protocol documentation, and a recent Token Terminal or DefiLlama snapshot of fee flow.
2. **Classify on primary economic function**, breaking ties in this order:
   - Fee or revenue source (where does the value flow that accrues to the token?)
   - Largest TVL or transaction-volume component
   - Marketing positioning (lowest weight — tie-breaker only)
3. **Assign chain_ecosystem** by largest-TVL deployment chain at snapshot date.
4. **Submit a PR** adding one row to `classification/snapshot.csv` and one file `decisions/<symbol>.md` with the rationale (template in [CONTRIBUTING.md](CONTRIBUTING.md)).

### 4.2 Reclassification

| Trigger | Action |
|---|---|
| Protocol pivots primary use case (e.g., a launchpad adds a DEX as primary product) | Sub-sector PR with effective date and rationale. |
| Token rebrand with no economic change (MATIC → POL) | Keep the same asset_id, update symbol, record the rename in `decisions/`. |
| Token migration via swap contract (LUNA → LUNA2/LUNC) | Mint a new asset_id; record the relationship in `decisions/`. |
| Chain ecosystem shift (largest-TVL chain changes) | Tag-only change. |

### 4.3 Cadence

Continuous PR review against `main`. The repository is tagged once per quarter (`v2026.Q2`, `v2026.Q3`, …) for consumers who require a stable reference. Between tags, `main` is always usable; tagged versions are immutable.

## 5. Out of scope (intentionally)

The following are deliberately excluded from v1.0 to keep the scope tight. Each is a potential future extension only if community demand emerges:

- **Universe filters** (mcap tier, ADV, listing venue) — these are properties of an asset's tradability, not its classification. Downstream consumers apply their own filters.
- **Regulatory tags** — jurisdiction-specific, fast-changing, and outside the scope of an industry classification.
- **Stablecoin internals** — peg mechanism details, reserve composition. We classify the *type* of stablecoin; deeper attribution is a separate dataset.
- **NFT collection-level classification** — collections are not fungible assets.
- **Per-asset Sharpe / IR / drawdown statistics** — these are derived analytics, not classification.

## 6. Versioning

| Component | Convention |
|---|---|
| Repository releases | Quarterly tags `vYYYY.QN` |
| `taxonomy.yaml` `version` field | SemVer; bumped on structural change (new sub-sector, code reshuffle) |
| `classification/snapshot.csv` | Tracks `main`; tagged with each release |

A consumer should pin to a specific release tag for reproducible backtests.

## 7. Comparable references

- MSCI / Coin Metrics / Goldman Sachs (2022). *Datonomy Methodology.*
- Bhojraj, Lee, Oler (2003). "What's My Line? A Comparison of Industry Classification Schemes for Capital Market Research." *Journal of Accounting Research.*
- S&P Global / MSCI. *Global Industry Classification Standard (GICS) Methodology.*
- FTSE Russell. *Industry Classification Benchmark (ICB) Ground Rules.*
