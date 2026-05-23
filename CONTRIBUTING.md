# Contributing

Thanks for helping curate the open industry classification for digital assets. Most contributions land in one of three buckets:

## 1. Add a new asset

The most common PR. About 5 minutes of work.

1. Add a row to [`classification/snapshot.csv`](classification/snapshot.csv) with columns:
   `asset_id, symbol, name, class_code, sector_code, sub_sector_code, chain_ecosystem`
2. If the assignment isn't obvious (i.e., a reasonable person could argue for a different sector), add a one-paragraph rationale in `decisions/<asset_id>.md` using the template below.
3. Open the PR. CI will check schema integrity. A maintainer (or any reviewer with two approved PRs) reviews and merges.

## 2. Reclassify an existing asset

When you have evidence the current classification is wrong.

1. Open an issue first if it's likely to be contested (e.g., a top-30 asset). Otherwise PR directly.
2. Update the row in `classification/snapshot.csv`.
3. **Required**: add or update `decisions/<asset_id>.md` with the new rationale and a brief note on what changed.
4. PRs that move more than 5 assets at once need an issue first.

## 3. Propose a new sub-sector

Adding a new sub-sector under an existing sector is a structural change.

1. Open an issue describing the candidate sub-sector. Required content:
   - **Name and proposed code** (use the next available `90`–`99` slot of the parent sector)
   - **Definition** (one paragraph)
   - **At least 5 candidate member assets** already in `snapshot.csv` or about to be added
   - **Evidence of positive within-group correlation** — at minimum, point to a date range where the candidates co-move more than they co-move with the parent sector's other members
2. After issue discussion, submit a PR that updates `taxonomy.yaml` and reassigns members.

## Decision document template

`decisions/<asset_id>.md`:

```markdown
# <SYMBOL> — <one-line summary>

**Decision**: classified as `<sub_sector_code>` (`<sub_sector_name>`).

**Date**: 2026-MM-DD
**Effective from snapshot**: vYYYY.QN

## Rationale

(2–4 sentences. What does this asset *do* economically? Where does fee or revenue
accrue? What were the alternative candidates and why were they rejected?)

## Evidence

(Optional but encouraged: links to whitepaper section, Token Terminal fee chart,
DefiLlama TVL breakdown. For empirical disputes, a small table of correlation
with peers in each candidate sector.)
```

## CI checks

Every PR runs:

- Schema validity of `taxonomy.yaml`
- No duplicate `asset_id` in `snapshot.csv`
- Every code in `snapshot.csv` exists in `taxonomy.yaml`
- Every active asset has a non-empty `chain_ecosystem`
- Wide matrices regenerate consistently from `snapshot.csv`

## Style

- Asset IDs are lowercase, hyphen-separated, stable across rebrands (`matic` stays `matic` even after the MATIC → POL rename — the asset_id never changes; only `symbol` updates).
- Symbols are uppercase and follow the most-traded ticker on Tier-1 CEXs.
- New asset PRs that bundle a sub-sector proposal are split into two separate PRs.

## Review SLA

Best-effort 7 days for new-asset PRs, 21 days for sub-sector proposals. Maintainers will tag stale PRs if review is blocked on missing information.

## Code of conduct

This is a technical reference. Discussion stays on the economic and empirical merits. Disputes are resolved by evidence (correlation tables, fee-flow charts, protocol docs), not by holdings or sentiment.
