# DYDX — dYdX

**asset_id**: `dydx`
**Current classification**: sector_code=`3010` (Decentralized Finance), sub_sector=`301020` (Derivatives Trading), chain_ecosystem=`COSMOS`
**Current sector cohesion**: +0.009, LOW (sector-level)

## What it is

dYdX is one of the original perpetual-futures DEXes. v3 ran as a StarkEx L2 rollup on Ethereum; v4 (launched late 2023) is a standalone Cosmos SDK appchain ("dYdX Chain") with an off-chain order book and on-chain settlement. Offers cross-margined perps on ~50+ markets. DYDX is the network's staking and governance token.

## Value accrual mechanism

On dYdX Chain, 100% of protocol trading fees are distributed to DYDX stakers (via validators) — this is one of the most direct real-yield distributions in DeFi. DYDX is also used to secure the chain via PoS staking + governance. Cash-flow profile: leveraged on perp-DEX volume; revenue volatile but distributed transparently.

## Economic siblings

HYPE (closest functional sibling — perp DEX on its own chain), ASTER (BNB-side perp DEX), SNX (synthetic / perp protocol). Distinct from spot DEXes.

## Classification verdict

- **Keep current**: `301020 Derivatives Trading`
- Rationale: Canonical perp DEX. Pair with HYPE, ASTER, SNX. Note dYdX is on its own Cosmos chain so chain_ecosystem=COSMOS — chain neutralization will separate it from ETH-perps like SNX.
