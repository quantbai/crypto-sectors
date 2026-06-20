# TIA — Celestia

**asset_id**: `tia`
**Current classification**: sector_code=`2020` (Blockchain Utilities), sub_sector=`202030` (Blockchain Networks), chain_ecosystem=`COSMOS`
**Current sector cohesion**: +0.015, LOW (parent sector)

## What it is

Celestia is the first dedicated modular data-availability (DA) layer,
launched October 2023. Cosmos-SDK based but its role is not to host
applications — rather to provide blobspace for rollups (Manta, Eclipse,
Movement, dYdX-fork chains, sovereign rollups) which post data
commitments and DA proofs.

## Value accrual mechanism

Rollups pay TIA to post blobspace; payments are denominated in TIA and a
portion of fees is burned EIP-1559-style. PoS staking secures the chain
(~17% APR, ~60% supply staked). Issuance ~6%. As blob count grows TIA
demand grows proportionally — clean usage-based accrual, but absolute fee
revenue is still small (~$0-1 M/month).

## Economic siblings (most similar tokens in our universe)

- EigenDA-adjacent assets (no direct universe peer)
- ATOM — Cosmos-SDK ecosystem cousin (different business model)
- (Distant) ETH — competing DA provider via 4844 blobs

## Classification verdict

- **Reclassify** to its own sub-group "Modular DA" (single-asset). If
  one-asset groups are not allowed in taxonomy v3, TIA is closer to ETH-
  L2 ecosystem beta than to L0 staking (DOT/ATOM) — modular-DA fates
  follow rollup adoption, not relay-chain staking.
- Rationale: TIA is a unique business model in the universe (selling DA
  blobspace, not application execution). Lumping it with DOT/ATOM
  obscures the DA-specific narrative beta (rollup launches, EIGEN-DA
  competitive pressure). If forced to merge, lean toward "Interop / DA
  infra" with ZRO.

Sources:
- https://celestia.org/
- https://medium.com/modular-money/celestia-making-tia-modular-money-to-power-a-sustainable-ecosystem-4864887a9271
