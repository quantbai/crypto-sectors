# TRX — TRON

**asset_id**: `trx`
**Current classification**: sector_code=`201010` (Smart Contract Platforms), chain_ecosystem=`TRX`
**Current sector cohesion**: -0.021, NEG (parent sector); TRX chain group +0.538 HIGH

## What it is

TRON is an EVM-compatible high-throughput L1 founded by Justin Sun
(2018), best known as the dominant settlement chain for USDT — ~75% of
all Tether supply circulates on TRC-20. Block production via DPoS with
27 Super Representatives.

## Value accrual mechanism

(1) Energy/bandwidth resource model: users either stake TRX to obtain
free resources, or burn TRX to pay for transactions; both create
structural demand. (2) Validator staking yield. The dominant driver is
USDT settlement fees, which generates ~$1B+/yr in TRX burn / fee
revenue. Because USDT transfers happen in any market regime, this
creates a cash-flow floor: TRX-beta to BTC has compressed from ~1.0
(2019-21) to ~0.30 (2024-26). See `decisions/trx.md` for full beta analysis.

## Economic siblings (most similar tokens in our universe)

- JST, SUN — TRON-ecosystem derivatives that share USDT-flow exposure (most direct siblings)
- (Cross-sector) Stablecoin issuers and centralized stablecoin chains — economic exposure is to stablecoin velocity, not L1 narrative

## Classification verdict

- **Keep current** sector classification (per existing `decisions/trx.md`), but flag as **economically distinct sub-group**: "USDT-settlement-driven defensive L1" — singleton in current universe.
- Rationale: defensive low-beta profile orthogonal to the SCP narrative cluster. Documented decision: capture via beta-factor exposure, not re-grouping.
