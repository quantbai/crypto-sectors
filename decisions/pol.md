# POL — Polygon as Network Scaling (Layer 2), not Smart Contract Platform

**Decision**: classified as `202010` (Network Scaling), not `201010` (Smart Contract Platforms).

**Date**: 2026-05-23
**Effective from snapshot**: v2026.Q2

## Rationale

POL is the canonical token of the Polygon ecosystem following the September 2024
1:1 migration from MATIC. The classification choice rests on Polygon's positioning
as a scalability layer for Ethereum-aligned applications, with most TVL and
transaction volume on Polygon PoS and Polygon zkEVM rather than on standalone
sovereign chains.

Polygon PoS is technically a sidechain (independent PoS consensus) rather than a
canonical Ethereum rollup. The classification is on *economic role*, not consensus
mechanism: applications, bridges, and developer tooling treat Polygon as an
Ethereum-adjacent scaling venue, the token's value accrual depends on Ethereum-
denominated TVL and activity, and the chain_ecosystem tag is set to `ETH` for
this reason.

## Alternative considered

`201010 Smart Contract Platforms`: rejected because the ecosystem is explicitly
positioned and used as an Ethereum extension rather than as a sovereign L1
competitor. Solana, Avalanche, and Sui are classified as `201010` because they
compete directly for Ethereum's developer base; Polygon does not.

## Note on sidechain vs rollup

A future taxonomy version may introduce a sub-sector distinction between true
rollups (Arbitrum, Optimism, Linea, zkSync) and sidechains (Polygon PoS, BSC-
style). The distinction is settlement-layer dependency — rollups inherit Ethereum
security; sidechains do not. v1.0 places both under `202010`; a sub-sector PR
that splits them is welcome with at least 5 members on each side.
