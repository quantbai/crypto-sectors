# FIL — Filecoin

**asset_id**: `fil`
**Current classification**: sector_code=`Information Technology (22)`, chain_ecosystem=`OTHER`
**Current sector cohesion**: -0.009, NEG (parent sector)

## What it is

Filecoin is the largest decentralized-storage network, built on top of IPFS.
Storage providers commit large amounts of disk and serve client deals via
proof-of-replication / proof-of-spacetime. Operates its own L1 (FVM enables
smart contracts since 2023).

## Value accrual mechanism

FIL is (1) collateral that storage providers stake to onboard sectors,
slashed for failed proofs; (2) payment from clients for storage deals;
(3) block reward / fee paid to providers; (4) burn via base-fee (EIP-1559
analog). Net supply growth is high (subsidy-funded providers), so value
accrual depends on storage-demand growth catching up with token issuance.

## Economic siblings (most similar tokens in our universe)

- AR (Arweave) — direct competitor, permanent storage
- WAL (Walrus) — newer Sui-native storage
- HNT (Helium), RNDR — DePIN/physical-resource siblings (provider-staking model)
- STORJ — older storage competitor

## Classification verdict

- **Reclassify** to "Decentralized Storage" sub-group with AR, WAL.
- Rationale: Storage is a distinct economic activity with provider-staking +
  client-payment + emission dynamics very different from oracles, compute,
  or identity. AR/FIL/WAL share the same demand driver (cost per GB-year
  vs AWS S3) and the same supply-side economics.
