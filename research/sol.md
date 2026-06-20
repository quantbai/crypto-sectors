# SOL — Solana

**asset_id**: `sol`
**Current classification**: sector_code=`201010` (Smart Contract Platforms), chain_ecosystem=`SOL`
**Current sector cohesion**: -0.021, NEG (parent sector)

## What it is

Solana is a high-throughput non-EVM monolithic L1 (single global state,
sub-second blocks, parallel execution via Sealevel). The dominant chain
for memecoin issuance (pump.fun) and the second-largest DeFi/stablecoin
chain after ETH.

## Value accrual mechanism

(1) Transaction fees split 50% burn / 50% to validators (post-SIMD-0096),
(2) staking yield from inflation (~5% currently, on a disinflation
schedule), (3) priority fees and MEV from high-frequency on-chain trading
(memecoin and perp DEX flow). Value accrual is more activity-coupled than
ETH because Solana's burn is dominated by priority fees rather than
base-fee, and the chain captures a large share of retail trading activity.

## Economic siblings (most similar tokens in our universe)

- ETH — competing general-purpose L1
- SUI / APT — non-EVM monolithic high-TPS chains with similar pitch
- AVAX — alt-L1 cohort, but EVM
- Solana DeFi ecosystem tokens (JTO, RAY, JUP) — direct beta to SOL activity

## Classification verdict

- **Keep current** (sector), but sub-group as "Non-EVM high-TPS general-purpose L1s" alongside SUI, APT (and arguably TON).
- Rationale: SOL's value-accrual is fundamentally activity-driven (priority fees / MEV) and tied to retail trading flow, materially different from ETH's deflationary base-fee + DeFi-collateral model. Should not be grouped with ETH for cohesion purposes.
