# WAL — Compute/Storage (DePIN), not Sui Ecosystem

**Decision**: classified as `compute_storage` in the `sector` field.

**Date**: 2026-06-10

## Context

WAL is the native token of Walrus, a decentralized blob-storage protocol built on Sui.
It was listed in 2025. In the `sector` field, WAL is placed in `compute_storage`
alongside FIL (Filecoin), AR (Arweave), and ICP (Internet Computer Protocol).

WAL's statistical home, however, is the Sui chain ecosystem: sui–wal demeaned
correlation 2024+ = 0.335, the strongest Sui-ecosystem pair. The storage-with-wal
candidate (fil, ar, wal) is statistically weak as a full-period group; storage-without-wal
(fil, ar) shows +0.318 demeaned correlation (STRONG).

## Considered alternatives

**Sui ecosystem / `smart_contract_platform`**: not a valid group placement in the
`sector` field schema. The function-beats-chain rule applies to application tokens: a
token whose economic design is usage-metered storage sells a specific resource,
regardless of host chain. Placing WAL in `smart_contract_platform` would mix its
economics with sovereign L1 gas/staking, which is wrong on first principles.

**`information_technology`** (broad catch-all): available as a fallback under the
residual-honesty rule. Rejected because a tighter group (`compute_storage`) exists and
WAL's protocol economics match it precisely.

**Standalone or merged with FIL+AR only**: fil+ar at n=2 cannot stand alone (n<3
validation floor). A three-member group requires a third token.

## Resolution rationale

`compute_storage` is defined as: *tokens metering decentralized compute/storage where
payment is burned/locked for resource usage.* The group members are:
- FIL — storage space on Filecoin, locked via storage deals
- AR — permanent storage on Arweave, one-time pay-to-store-forever
- ICP — cycles-burn model for cloud compute on Internet Computer
- WAL — blob-storage capacity on Walrus, with WAL staked to storage nodes and
  payment settled per epoch

WAL's economics match the group definition precisely: storage-capacity tokens whose
value accrues from resource-usage payments, not from chain fee burn or ecosystem TVL.

The Sui-chain correlation (sui–wal 0.335) is a 2025-listing artifact: young assets
co-move with their host chain's beta during the early listing period. Classification
follows protocol economics, not the transient correlation of a new listing to its host
chain. WAL is registered in the exception register as a known short-history misfit
(listed 2025; WAL protocol beta vs Sui-chain will decay as it matures).

## Cross-reference

See `decisions/sector-field-okx-2026-06.md` §Amendment 4 and §exception-register
entry for WAL. `validation/sector_okx/REPORT.md` §group-definitions for the
`compute_storage` group.
