# SNX — Synthetix

**asset_id**: `snx`
**Current classification**: sector_code=`3010` (Decentralized Finance), sub_sector=`301020` (Derivatives Trading), chain_ecosystem=`ETH`
**Current sector cohesion**: +0.009, LOW (sector-level)

## What it is

Synthetix is a synthetic-asset protocol that lets users mint synths (sUSD, sBTC, sETH, etc.) by staking SNX as collateral. Its v3 architecture decomposed the protocol into liquidity pools backing markets, and Synthetix Perps powers perpetual futures on Optimism, Base, and Arbitrum — often used as a backend by front-ends like Kwenta and dHEDGE.

## Value accrual mechanism

SNX stakers act as collateral providers for the debt pool. They mint sUSD, take on a share of the global synth debt, and in return earn (a) trading fees from synth + perp trading, and (b) inflationary SNX rewards. Value capture is therefore real-yield from derivatives flow, but stakers bear oracle risk and shared-debt risk. Token has high beta to perp-DEX volume.

## Economic siblings

DYDX, HYPE, ASTER (perp DEXes); historically dYdX is closest in derivatives flow. Distinct from spot DEX governance (UNI/CRV) because product is leverage/synthetics rather than spot AMM.

## Classification verdict

- **Keep current**: `301020 Derivatives Trading`
- Rationale: Synthetic assets and perps are derivatives products. Belongs in the perp/derivatives sub-cohort with DYDX, HYPE, ASTER, though SNX's synth-pool model differs from order-book perp DEXes.
