# PENDLE — Pendle Finance

**asset_id**: `pendle`
**Current classification**: sector_code=`3010` (Decentralized Finance), sub_sector=`301060` (Asset Management), chain_ecosystem=`ETH`
**Current sector cohesion**: +0.009, LOW (sector-level)

## What it is

Pendle is a yield-tokenization protocol that splits yield-bearing assets (stETH, sUSDe, GLP, eETH, etc.) into Principal Tokens (PT, zero-coupon claim) and Yield Tokens (YT, claim on future yield). Users trade fixed yield via PT, speculate on yield rates via YT, or LP into Pendle AMM pools. Pendle became the dominant venue for LRT and points-farming flows in 2024–2025.

## Value accrual mechanism

PENDLE follows a Curve-style veToken model: lock PENDLE → vePENDLE → vote-direct emissions to pools, earn 80% of swap fees + a share of YT fees + voter bribes. Real-yield accrual is meaningful (active perpetual revenue). High beta to LRT/points/yield-cycle activity.

## Economic siblings

CVX (other yield-aggregation / governance-emission protocol). Less direct: ETHFI, ENA (because their underlying yield-bearing tokens are major Pendle markets). Pendle is structurally adjacent to LRT/stablecoin issuers because its volume depends on their existence.

## Classification verdict

- **Keep current**: `301060 Asset Management`
- Rationale: Yield derivative/tokenization protocol. Cohort with CVX for "yield extraction / boost / derivatives" sub-group.
