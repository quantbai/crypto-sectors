# LDO — Lido DAO

**asset_id**: `ldo`
**Current classification**: sector_code=`3010` (Decentralized Finance), sub_sector=`301090` (Liquid Staking — Governance), chain_ecosystem=`ETH`
**Current sector cohesion**: +0.009, LOW (sector-level)

## What it is

Lido is the largest liquid-staking protocol, primarily for ETH (issuing stETH) and previously Solana, Polygon, and others (most non-ETH deployments wound down). Users deposit ETH → Lido stakes it via a permissioned node-operator set → receive stETH (rebasing) or wstETH (wrapped, non-rebasing). LDO is the governance token of the DAO that controls operator selection, fee parameters, and treasury.

## Value accrual mechanism

Lido takes a 10% cut of ETH staking rewards: 5% to node operators, 5% to the DAO treasury. LDO holders govern the DAO but have no direct cash-flow claim today; value capture is treasury-revenue accumulation + governance optionality over a multi-billion-dollar staking franchise. There has been ongoing debate about staker buybacks; not currently active.

## Economic siblings

JTO (Jito, Solana LST issuer — closest mechanical sibling). Adjacent: ETHFI (liquid restaking on top of ETH staking) and EIGEN (restaking infra). All four share a "staking yield + protocol fee" return driver distinct from spot trading or lending.

## Classification verdict

- **Keep current**: `301090 Liquid Staking — Governance`
- Rationale: Canonical LST governance token. Group with JTO (and possibly ETHFI/EIGEN if we treat restaking as a single staking-yield cohort).
