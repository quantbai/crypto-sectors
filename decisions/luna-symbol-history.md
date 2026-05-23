# LUNA — symbol history and asset_id discipline

**Decision**: the symbol `LUNA` has referred to two distinct assets. We use
asset_ids `terra-luna-original` and `terra-luna-2` to keep them separate, and
the symbol field tracks whichever the most recent canonical use is.

**Date**: 2026-05-23
**Effective from snapshot**: v2026.Q2

## Background

- 2019-04 to 2022-05: `LUNA` referred to the Terra Classic network's native token. After the May 2022 collapse, the network was renamed Terra Classic and the token was rebranded to `LUNC`. This is `asset_id = terra-luna-original`.
- 2022-05 onwards: A new chain launched with a freshly minted token, originally labeled `LUNA2` and now commonly traded as `LUNA`. This is `asset_id = terra-luna-2`.

The two assets are **not** the same instrument:
- No 1:1 swap contract relates them.
- The new chain has different validators, different supply, no historical state from the original Terra.
- LUNC holders received a small airdrop allocation of LUNA2, but the bulk of value did not transfer.

## Why this matters for users of this dataset

Anyone joining a price series labeled `"LUNA"` from before and after May 2022
risks stitching two unrelated assets into a single time series — the pre-collapse
returns belong to a defunct asset, the post-launch returns belong to a new one.

**Recommendation for backtests**:
- Use `asset_id`, not `symbol`, as the join key against this classification.
- For pre-2022-05 LUNA data, use `asset_id = terra-luna-original`.
- For post-2022-05 LUNA data, use `asset_id = terra-luna-2`.
- Do not splice their return series without explicit acknowledgment.

## Wide-matrix implications

In `classification/wide/*.parquet`, columns are asset_ids. `terra-luna-original`
and `terra-luna-2` appear as separate columns with non-overlapping date ranges
(the original's effective period ends 2022-05-12; the new chain begins 2022-05-28).

If a downstream user joins by symbol, the two assets will collide. This is why
this repository uses asset_id consistently and recommends consumers do the same.

## Related cases

- `dydx-v3` vs `dydx`: dYdX migrated from an Ethereum-based v3 to a sovereign Cosmos chain (v4) in October 2023. Treated as two asset_ids for the same reasons.
- `matic` vs `pol`: 1:1 contract migration with full economic continuity. Treated as the *same* asset, with `symbol` updated and `name` rewritten. No separate asset_id.
