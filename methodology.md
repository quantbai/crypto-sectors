# Methodology

> Version 1.0.0 · Release date 2026-05-24

## 1. Purpose

A reference industry classification for digital assets, usable for:

1. **Cross-sectional sector neutralization** of alpha signals (`group_neut`).
2. **Risk attribution** — decomposing returns into sector, chain, and idiosyncratic components.
3. **Peer-group comparison** — fundamental and technical metrics are only meaningful relative to peers performing a similar economic function.
4. **Comparability with established institutional research** — the 6-digit `CCSSXX` positional code format was chosen to make potential future crosswalks to institutional classification systems tractable. See §3.2 for the affiliation disclaimer.

## 2. Design principles

| # | Principle | Why |
|---|-----------|-----|
| 1 | **Single-leaf assignment** within the hierarchy | An asset belonging to multiple groups is unusable for `group_neut`. We accept the cost: borderline assets are placed in their dominant economic function, with the rationale recorded in `decisions/`. |
| 2 | **Theory-driven, empirically validated** | The taxonomy starts from established economic-function definitions in the institutional classification literature (see §7). Sectors are not discovered from clustering — that would overfit. We then validate that same-sector returns co-move more than cross-sector returns. |
| 3 | **Orthogonal tags alongside the hierarchy** | Chain-ecosystem effects in crypto can rival sector effects. Forcing them into the hierarchy distorts the tree; treating them as a cross-cutting tag preserves both axes. |
| 4 | **Auditable per-asset decisions** | Every non-trivial classification has a markdown file in `decisions/` recording the rationale. Disputes become PRs with evidence. |

## 3. Hierarchy

Three levels:

```
Class (2-digit, 4 entries)            ── reporting & risk-regime boundary
  └── Sector (4-digit, 14 entries)    ── primary group-neutralization axis
        └── Sub-sector (6-digit)      ── attribution & fine-grained neutralization
```

### 3.1 Why three levels (and not two, or four)

The choice tracks the precedent set by established equity-market classification systems (cited in §7) — both are four-level systems with 5,000+ constituents — adjusted downward by one level because the digital-asset universe is roughly an order of magnitude smaller.

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

Sub-sector codes ending `90`–`99` are community extensions. They are visually distinguishable (e.g., `301090` for Liquid Staking) and reserve the `00`–`89` range for potential future alignment with institutional classification baselines.

Uses a 6-digit positional code format (`CCSSXX`) as a structural convention. This project has no affiliation with, and makes no claim of mapping compatibility to, Datonomy, GICS, or ICB. The format choice exists to make potential future crosswalks tractable, not to guarantee one today.

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

**Point-in-time (PIT) immutability contract.** The `effective_from` field in `classification/snapshot.csv` records the date from which each classification row applies. Historical published panels are immutable. Reclassifications create new rows in `snapshot.csv` with a later `effective_from`; they never modify rows for past dates. A backtest pinned to a release tag (e.g. `git checkout v1.0.0`) will reproduce exactly across future taxonomy bumps.

> **Warning**: running a historical backtest against `main` after a reclassification PR is merged WILL show different results for pre-reclass dates. For reproducible historical backtests, always check out a release tag.

**`effective_from` semantics**: cells in the wide matrix dated before an asset's `effective_from` are `NaN`, meaning "asset not yet classified under this schema version" — not "asset does not exist". See [SCHEMA.md](SCHEMA.md) for the full null policy.

### 4.3 Cadence

Continuous PR review against `main`. The repository is tagged once per quarter (`v2026.Q2`, `v2026.Q3`, …) for consumers who require a stable reference. Between tags, `main` is always usable; tagged versions are immutable.

## 5. Out of scope (intentionally)

The following are deliberately excluded from v1.0 to keep the scope tight. Each is a potential future extension only if community demand emerges:

- **Investable filters** (mcap tier, ADV, listing venue) — these are properties of an asset's tradability, not its classification. This repository defines a **coverage universe** (which assets are classified); the **investable universe** (which assets a specific strategy trades) is determined downstream by each consumer applying their own filters. See [UNIVERSE.md](UNIVERSE.md) for coverage criteria.
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

## 7. References

Academic and industry references that informed the design. Inclusion here is academic citation; no endorsement or affiliation is implied or claimed.

- MSCI, Coin Metrics, and Goldman Sachs (2022). *Datonomy Methodology.* (Digital-asset classification reference. Uses a 6-digit positional code format (`CCSSXX`) as a structural convention. This project has no affiliation with, and makes no claim of mapping compatibility to, Datonomy, GICS, or ICB. The format choice exists to make potential future crosswalks tractable, not to guarantee one today.)
- Bhojraj, S., Lee, C., and Oler, D. (2003). "What's My Line? A Comparison of Industry Classification Schemes for Capital Market Research." *Journal of Accounting Research*, 41(5).
- S&P Global and MSCI. *Global Industry Classification Standard (GICS) Methodology.* (Cross-asset precedent for multi-level hierarchical industry classification.)
- FTSE Russell. *Industry Classification Benchmark (ICB) Ground Rules.*
- Hoberg, G., and Phillips, G. (2016). "Text-Based Network Industries and Endogenous Product Differentiation." *Journal of Political Economy*.

### Trademark notice

GICS is a registered trademark of S&P Global and MSCI Inc. Datonomy is a trademark of MSCI Inc. ICB is a trademark of FTSE International Limited. WorldQuant and BRAIN are trademarks of WorldQuant LLC. All other trademarks are the property of their respective owners. This project is independent of, and has no business relationship with, any of these organizations.
