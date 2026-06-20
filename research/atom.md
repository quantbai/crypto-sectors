# ATOM — Cosmos Hub

**asset_id**: `atom`
**Current classification**: sector_code=`2020` (Blockchain Utilities), sub_sector=`202030` (Blockchain Networks), chain_ecosystem=`COSMOS`
**Current sector cohesion**: +0.015, LOW (parent sector)

## What it is

ATOM is the native asset of the Cosmos Hub, the original IBC-enabled
relay zone in the Cosmos / Tendermint ecosystem (live 2019). Cosmos
ecosystem chains (Osmosis, Celestia, dYdX, Injective, Sei, etc.) use the
same SDK and IBC messaging; Cosmos Hub provides ICS (Interchain Security)
to consumer chains.

## Value accrual mechanism

PoS staking (~14% APR, ~65% supply staked). Issuance dynamic (target
67% bonded). Hub fees come from: (1) base ATOM tx, (2) consumer-chain
fees under ICS (Stride, Neutron pay portion of staking yield to ATOM
stakers). The 2024 "ATOM 2.0" proposal pivoting to a more revenue-
sharing model failed; the simpler ICS model is what's live. Returns
driven by Cosmos ecosystem activity and macro-DeFi beta.

## Economic siblings (most similar tokens in our universe)

- DOT — direct L0 competitor (relay/parachain model)
- TIA — Celestia is a Cosmos-SDK chain; close ecosystem cousin
- OSMO, INJ — Cosmos-SDK app chains (if in universe)

## Classification verdict

- **Reclassify** — from 202030 to a "Cross-chain Interop / L0" sub-group
  with DOT.
- Rationale: ATOM and DOT are the cleanest 2-asset L0 sub-group (relay-
  chain + connected ecosystem model, staking-driven). Both compete on
  shared-security / interop primitives. TIA is technically a Cosmos-SDK
  chain but is a different (modular DA) business model — keep separate.

Sources:
- https://hub.cosmos.network/
- https://github.com/cosmos/cosmos-sdk
