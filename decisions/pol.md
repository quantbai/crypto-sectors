# POL — Smart Contract Platform, not Eth Scaling

**Decision**: classified as `smart_contract_platform` in the `sector` field.

**Date**: 2026-06-10

## Rationale

POL is the canonical token of the Polygon ecosystem following the September 2024
1:1 migration from MATIC. The classification rests on Polygon's security architecture:
Polygon PoS operates its own validator set (125+ validators, independent PoS consensus)
and does NOT post fraud proofs or validity proofs to Ethereum for per-block security;
Ethereum is a data checkpoint, not a security source.

The `sector` field's settlement-dependence rule requires that fee revenue AND security
inherit from Ethereum settlement — Polygon PoS fails this test on chain data. Despite
Polygon being positioned as an Ethereum-adjacent scaling venue, its economics are those
of a sovereign platform: POL stakes secure the Polygon PoS validator set and the
AggLayer sequencer set — staking/governance economics of a sovereign platform,
not rollup sequencer fee economics derived from Ethereum blockspace.

## Alternative considered

**`eth_scaling`**: rejected. The settlement-dependence rule requires per-block security
derived from Ethereum. Polygon PoS operates independent PoS consensus; Ethereum is a
data checkpoint only. Rollups (ARB, OP, STRK, ZK, LINEA) all post proofs to Ethereum
and derive per-block finality from Ethereum settlement — Polygon PoS does not.

Statistical confirmation: POL–L2 demeaned correlation 2024+ = −0.049. POL co-clusters
with `ada` at 0.84 bootstrap co-cluster frequency (old-guard alt cohort, not EVM-L2
block). Within-L2 cohesion excluding POL = 0.180 (STRONG); with POL it collapses to
0.104. Moving POL to `smart_contract_platform` strengthens `eth_scaling` cohesion from
0.104 to 0.180.

## Note on sidechain vs rollup

Polygon PoS is technically a sidechain (independent PoS consensus) rather than a
canonical Ethereum rollup. A future taxonomy version may introduce a sub-sector
distinction between true rollups (ARB, OP, LINEA, ZK) and sidechains. This
classification places POL in `smart_contract_platform` and the distinction is recorded
in the exception register.

## Cross-reference

See `decisions/sector-field-okx-2026-06.md` for the audit record.
`validation/sector_okx/REPORT.md` for quantitative detail.
