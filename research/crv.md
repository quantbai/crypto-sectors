# CRV — Curve DAO

**asset_id**: `crv`
**Current classification**: sector_code=`3010` (Decentralized Finance), sub_sector=`301010` (Decentralized Exchanges), chain_ecosystem=`ETH`
**Current sector cohesion**: +0.009, LOW (sector-level)

## What it is

Curve is an AMM optimized for low-slippage swaps between like-priced assets — stablecoin↔stablecoin, ETH↔stETH, BTC-wrapped pairs. Curve also operates crvUSD (a CDP-style stablecoin with LLAMMA liquidation curves) and LlamaLend isolated lending markets.

## Value accrual mechanism

CRV emissions are directed to pools via gauge votes; vote weight is determined by veCRV (vote-escrowed CRV, locked up to 4 years). veCRV holders earn 50% of swap fees plus bribes paid in external tokens for vote-direction. crvUSD borrowing fees also flow to veCRV stakers. This makes CRV one of the most explicit "real yield" governance tokens — fees + bribes accrue directly to lockers — but the veToken lockup creates highly path-dependent supply dynamics ("Curve Wars").

## Economic siblings

UNI, CAKE, AERO (other AMM governance tokens — AERO is the closest, as Aerodrome is a Solidly/ve-fork of Curve); CVX (Convex aggregates veCRV power). Adjacent because of crvUSD: SKY/ENA on the stablecoin axis.

## Classification verdict

- **Keep current**: `301010 Decentralized Exchanges`
- Rationale: Primary product is a DEX. crvUSD/LlamaLend are secondary. Strong economic link to CVX (which should remain in 301060 Asset Management / yield aggregator).
