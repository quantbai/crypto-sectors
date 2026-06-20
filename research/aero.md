# AERO — Aerodrome Finance

**asset_id**: `aero`
**Current classification**: sector_code=`3010` (Decentralized Finance), sub_sector=`301010` (Decentralized Exchanges), chain_ecosystem=`ETH`
**Current sector cohesion**: +0.009, LOW (sector-level)

## What it is

Aerodrome is the dominant AMM/DEX on Base (Coinbase's L2). It's a fork of Velodrome (which was a Solidly fork by the same Dromos Labs team), running a Curve-style vote-escrow gauge model: lock AERO → veAERO NFT → vote-direct AERO emissions to pools and earn 100% of those pools' trading fees + bribes [CoinGecko explainer](https://www.coingecko.com/learn/what-is-aerodrome-finance-aero-base). Aerodrome and Velodrome are merging into a unified "Aero" platform in 2026.

## Value accrual mechanism

Pure ve-DEX economics: veAERO lockers receive trading fees, bribes paid by external projects for emission direction, and rebases. Real-yield is meaningful — fees and bribes accrue directly to lockers. AERO emissions inflate supply but veAERO lockers offset via the bribe/fee capture loop.

## Economic siblings

CRV (closest — same vote-escrow gauge model; Aerodrome is effectively "Curve on Base"), UNI/CAKE/SUN/RAY (other AMM governance tokens). CVX is the wrapper analog but no equivalent meta-aggregator exists for AERO at our universe scale.

## Classification verdict

- **Keep current**: `301010 Decentralized Exchanges`
- Rationale: Spot AMM with ve-tokenomics. Belongs in DEX cohort with UNI, CRV, CAKE, SUN, RAY.
