# BERA — Berachain

**asset_id**: `bera`
**Current classification**: sector_code=`201010` (Smart Contract Platforms), chain_ecosystem=`OTHER`
**Current sector cohesion**: -0.021, NEG (parent sector)

## What it is

Berachain is an EVM-equivalent L1 with a novel "Proof-of-Liquidity"
(PoL) consensus, mainnet launched February 6, 2025. Three-token model:
BERA (gas / chain security), BGT (governance / non-transferable,
earned by liquidity providers), HONEY (native stablecoin). Validators
direct BGT emissions to reward vaults, aligning chain security with
DeFi liquidity provision.
[docs.berachain.com/learn/what-is-proof-of-liquidity, decrypt.co/resources/what-is-berachain-proof-of-liquidity-blockchain]

## Value accrual mechanism

(1) BERA is burned on every transaction (deflationary, similar to
EIP-1559), (2) BERA is the staking asset for validators, (3) BGT is
redeemable 1:1 for BERA (one-way), creating a structural sink as DeFi
emissions are converted to spendable BERA. The PoL flywheel:
liquidity providers earn BGT → BGT redeemed for BERA → BERA staked
or burned → security increases → more liquidity.

## Economic siblings (most similar tokens in our universe)

- ETH — EVM, fee-burn, staking — closest mechanic peer
- AVAX — EVM L1 with similar fee burn + staking
- MON — 2025-vintage EVM challenger
- (Cross-sector) Curve / Convex governance — BGT-bribe / vote-escrow economic dynamics

## Classification verdict

- **Keep current** sector, sub-group as "DeFi-native EVM L1s" — BERA's economic identity is "chain whose security IS its DeFi liquidity". Returns will track its DeFi ecosystem health more than generic L1 narrative.
- Rationale: BERA's PoL mechanic creates DeFi-flow-coupled returns distinct from generic EVM L1s. Worth flagging as economically distinct from MON / AVAX even though they share VM.
