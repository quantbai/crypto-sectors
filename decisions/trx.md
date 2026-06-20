# TRX — Value Transfer (USDT-settlement-driven defensive beta)

**Decision**: classified as `value_transfer` in the `sector` field.

**Date**: 2026-06-10
**Effective from snapshot**: v3.0.0

## Rationale

TRX is the native token of the TRON network, which has become the dominant
settlement layer for Tether (USDT). As of 2026, approximately 75% of all
USDT supply is issued on TRC-20 (TRON), with daily transaction volume on
TRON regularly exceeding all other chains combined for stablecoin transfers.

This gives TRX a distinct economic profile relative to peer L1s:

**Defensive (low) beta to BTC, NOT counter-cyclical**

Empirical 365-day rolling beta of TRX to BTC over 2019-2026:

| Window end | beta_to_BTC |
|------------|-------------|
| 2019-06    | +1.16       |
| 2020-12    | +1.01       |
| 2022-05    | +0.90       |
| 2023-05    | +0.62       |
| 2024-11    | +0.29       |
| 2026-05    | +0.30       |

Full-sample beta = +0.83 (positive). 0 of 2,541 monthly observations show
negative beta. TRX is not literally inverse to BTC — when BTC drops, TRX
usually drops too. But the magnitude of drop has compressed dramatically:
TRX beta has declined from ~1.0 in the 2019-2021 period to ~0.30 in the
2024-2026 period.

**Why**: USDT settlement fees on TRON accrue independently of broader crypto
market direction. In bear markets, when capital flows OUT of risk assets and
INTO stablecoins, TRX still captures the resulting fee flow. This cash-flow
floor caps TRX's downside in drawdown regimes while attenuating its upside in
risk-on regimes.

## Classification rationale: `value_transfer`

TRX's economics are anchored to USDT value transfer: the chain's dominant
activity is peer-to-peer and cross-border USDT transmission. Value accrual
to TRX is through block-production fees and energy/bandwidth resource
consumption, where the overwhelming share of activity is stablecoin transfers
rather than smart-contract execution. This maps to `value_transfer` (native
currencies of non-smart-contract-primary chains whose primary purpose is
store-of-value and payment/settlement).

The reaudit (2026-06-17) moved TRX from `captive_franchise` to `value_transfer`
on economics-first grounds: TRON is not a captive franchise of a single
intermediary (Binance, Telegram, Crypto.com) — it is an open settlement rail
whose USDT flows are not captive to any single platform. The economics are
value-transfer (open settlement), not franchise-fee-burn.

## Alternative considered

**`captive_franchise`**: an earlier placement grouped TRX with BNB/CRO/TON on
the grounds of defensive beta and realized cash-flow stability. Rejected on
economics-first review: TRON's USDT settlement is an open, permissionless rail
used by millions of independent actors — structurally different from Binance's
or Telegram's closed-ecosystem franchise. The defensive beta is real but is
better explained by stablecoin-settlement cash-flow floors (value_transfer
economics), not franchise captivity.

**`smart_contract_platform`**: rejected. Although TRON supports smart contracts,
the dominant activity and value driver is USDT transfer, not general-purpose
smart-contract execution.

## Implication for group_neut

TRX is demean-grouped within `value_transfer` alongside BTC, BCH, LTC, XRP, XLM,
RVN. The production OTHER-collapse kernel applies; with n=7 the group exceeds the
min-3-member threshold on most trading days.

## Cross-reference

See `decisions/sector-field-okx-2026-06.md` for the full audit record.
`validation/sector_okx/REPORT.md` §exception-register for quantitative detail.
