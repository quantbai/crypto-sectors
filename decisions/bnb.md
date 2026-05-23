# BNB — Private Exchange token, not Smart Contract Platform

**Decision**: classified as `302030` (Private Exchanges), not `201010` (Smart Contract Platforms).

**Date**: 2026-05-23
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
even when an L1 chain is attached.

The chain_ecosystem tag is set to `BNB` to reflect the technical chain affiliation.
A consumer running sector-neutral analysis will neutralize BNB against other
exchange tokens; a consumer running chain-neutral analysis will neutralize it
against other BSC ecosystem assets. Both treatments are correct in their
respective contexts — that is the purpose of having orthogonal tags.

## Alternative considered

`201010 Smart Contract Platforms`: rejected because empirical co-movement with
peer SCPs (ETH, SOL, AVAX) is materially weaker than co-movement with peer
exchange tokens. The BSC chain activity is a contributing factor to BNB's value
but not the primary one, especially during periods of exchange-specific news
flow.

## Related decision

CRO (Cronos) and OKB follow the same logic. NEXO is classified `302010 Intermediated Lending` rather than `302030` because its primary product is a lending platform, not an exchange.
