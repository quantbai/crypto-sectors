# ENA — Ethena

**asset_id**: `ena`
**Current classification**: sector_code=`3010` (Decentralized Finance), sub_sector=`301040` (Stablecoin Issuers), chain_ecosystem=`ETH`
**Current sector cohesion**: +0.009, LOW (sector-level)

## What it is

Ethena is a synthetic-dollar issuer. Its USDe stablecoin is backstopped by a delta-neutral basis trade: long spot ETH/BTC/SOL/LST collateral hedged with short perpetual futures on centralized derivatives venues, with the resulting cash + funding spread providing both the dollar peg and a native yield (sUSDe). Ethena also issues USDtb (Treasury-backed) and is expanding into iUSDe (institutional) plus the Converge L1 with Securitize.

## Value accrual mechanism

ENA is the governance token. The protocol earns funding-rate income + staking yield on collateral; a fee-switch mechanism routes a portion of revenue to staked ENA (sENA) holders once activated. Value capture is highly cyclical with perp funding and USDe scale. ENA has tighter cash-flow linkage than most DeFi governance tokens.

## Economic siblings

SKY (CDP/stablecoin issuer, different mechanism but same "stablecoin-issuer DAO" archetype), RSR (basket-backed dollar issuer), FF (delta-neutral collateralization is very close — see ff.md).

## Classification verdict

- **Keep current**: `301040 Stablecoin Issuers`
- Rationale: Synthetic-dollar issuer with funding-yield economics. Cohort with SKY, RSR, FF. FF in particular shares a near-identical delta-neutral architecture.
