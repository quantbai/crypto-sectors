# research/

Per-asset deep-research notes. Each markdown documents an asset's
economic positioning, value-accrual mechanism, and proposed
re-classification (if applicable).

This folder is the input to **taxonomy v3** — a re-grouping pass driven by
empirical cohesion + economic fundamentals, NOT just nominal industry
labels. Background: §4.3 cohesion analysis (2026-05-27) showed that
several "sectors" (Smart Contract Platforms, DeFi, Information Technology)
have near-zero or negative within-group correlation despite passing the
§4.4 group_neut variance-reduction test. The current Datonomy-style
taxonomy is statistically valid but economically loose; many "sector" labels
are catch-alls rather than genuine same-economic-mechanism groupings.

## Per-asset markdown template

```markdown
# <SYMBOL> — <Name>

**asset_id**: `<asset_id>`
**Current classification**: sector_code=`<X>` (`<sector_name>`), chain_ecosystem=`<Y>`
**Current sector cohesion**: <e.g., "+0.009, LOW"  — from §4.3 cohesion table>

## What it is

[1-3 sentences. Cite source if web-fetched.]

## Value accrual mechanism

[How does the token capture value? Fees / governance / burn / staking / etc. 2-4 sentences.]

## Economic siblings (most similar tokens in our universe)

[List 2-5 other tokens that this one most closely resembles economically.
Don't restrict to current sector — find true siblings.]

## Classification verdict

- **Keep current** / **Reclassify**
- If reclassify: suggested new sector (code or descriptive sub-group name)
- Rationale: [1-2 sentences]
```

## Coverage status

This research pass targets ~120 assets in sectors with LOW or NEG cohesion.
Already-cohesive sectors (Value Transfer Coins, Intermediated Finance,
Media Services) are skipped — those are correctly classified.

| Subagent | Sector(s) | Coin count | Status |
|----------|-----------|------------|--------|
| A | Smart Contract Platforms | 31 | running |
| B | Decentralized Finance | 32 | running |
| C | Information Technology + App Utilities | 26 | running |
| D | Specialized Coins + Metaverse + Blockchain Utilities | 33 | running |
