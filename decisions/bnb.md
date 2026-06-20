# BNB — Exchange equity / captive franchise, not Smart Contract Platform

**Decision**: `sector = captive_franchise` (exchange-equity / captive off-chain operator feeding fees — Binance).

**Date**: 2026-05-23  
**Revised**: 2026-06-20 (v3 flat-sector pivot)  
**Effective from snapshot**: v2026.Q2

## Rationale

BNB is the native token of both the Binance centralized exchange and the BNB
Smart Chain. The classification is made on the dominant value-accrual mechanism:
BNB's price has historically tracked Binance corporate health, fee discounts,
and quarterly token-burn events more closely than BNB Smart Chain TVL or
transaction fees.

This places BNB in the same economic category as other exchange-affiliated
tokens (OKB, KCS, GT, BGB) — all of which derive value primarily from a
centralized exchange's discretion over burns, listings, and ecosystem subsidies,
even when an L1 chain is attached. These tokens are best understood as
exchange equity proxies: the exchange captures fees off-chain and recycles a
portion back to token holders, making the exchange operator the ultimate
value gatekeeper.

## Alternative considered

`Smart Contract Platforms` (e.g. ETH, SOL, AVAX): rejected because empirical
co-movement with peer SCPs is materially weaker than co-movement with peer
exchange tokens. The BSC chain activity is a contributing factor to BNB's value
but not the primary one, especially during periods of exchange-specific news
flow.

## Related decisions

CRO (Cronos) and OKB follow the same logic and are also labeled
`captive_franchise`. NEXO is classified `intermediated_lending` rather than
`captive_franchise` because its primary product is a lending platform, not an
exchange.

See `decisions/sector-field-okx-2026-06.md` for the full sector taxonomy and
governance charter. Empirical validation is at `validation/sector_okx/REPORT.md`.
