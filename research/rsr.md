# RSR — Reserve Rights

**asset_id**: `rsr`
**Current classification**: sector_code=`3010` (Decentralized Finance), sub_sector=`301040` (Stablecoin Issuers), chain_ecosystem=`ETH`
**Current sector cohesion**: +0.009, LOW (sector-level)

## What it is

Reserve is a decentralized platform for "Asset-Backed Currencies" (RTokens) — anyone can deploy an over-collateralized basket-backed stablecoin or token-folio (DTF) [Reserve docs](https://reserve.org/protocol/reserve_rights_rsr/). RSR is the protocol's backstop/insurance and governance token. Issued RTokens include eUSD, USD3, ETH+, hyUSD, plus DTFs like CoinMarketCap's CMC20.

## Value accrual mechanism

Stake RSR on a specific RToken → provide first-loss insurance capital. In return, stakers earn a share of that RToken's revenue (collateral yield, typically Aave/Compound supply rates on backing assets). Unstaking has a 7–30 day delay. If an RToken's collateral fails, staked RSR is auctioned to make holders whole — slashing-style insurance. Governance is per-RToken. Active RFC-1269 (Dec 2025) proposes burning ~30B unused RSR.

## Economic siblings

SKY (CDP/stablecoin issuer), ENA (synthetic-dollar issuer), FF (delta-neutral collateralization). Closest mechanical sibling: SKY — both are over-collateralized stablecoin issuers with a backstop token.

## Classification verdict

- **Keep current**: `301040 Stablecoin Issuers`
- Rationale: Issuer governance/insurance token for a family of asset-backed stablecoins. Cohort with SKY, ENA, FF.
