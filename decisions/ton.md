# TON — Captive Franchise, not Smart Contract Platform

**Decision**: classified as `captive_franchise` in the `sector` field.

**Date**: 2026-06-10
**Effective from snapshot**: v3.0.0

## Context

TON (The Open Network) is the Layer 1 blockchain developed and promoted by Telegram.
In the `sector` field, it is placed in `captive_franchise` alongside BNB and CRO.

The initial design kept TON in `smart_contract_platform` on the argument that TON's
token economics are sovereign-L1 gas/staking and Telegram distribution is a demand
channel, not a contractual cash-flow claim on an intermediary. Amendment 3 reversed
this placement.

## Considered alternatives

**`smart_contract_platform`**: rejected in Amendment 3. TON's *realized* token economics
are inseparable from Telegram's distribution. Telegram has 950M+ monthly active users;
TON's USDT issuance and payment flows are not aspirational — they are the measured,
current activity on the chain. The distinction between "demand channel" and "captive
franchise" collapses when the franchise is Telegram and the chain has no meaningful
activity outside it. TON's BTC beta (2024+, ~0.89) is materially below the live-basket
range (1.17–1.38) and consistent with the defensive/captive cluster, not with sovereign
growth-L1s.

## Resolution rationale

The `captive_franchise` group is defined as: *quasi-equity of an established captive
distribution franchise monetized via fee/burn — where the franchise has realized (not
aspirational) captive flow.*

TON passes this test:

1. **Telegram distribution is the chain's realized demand.** Telegram's ~1B user base
   drives TON's USDT volume and wallet adoption; there is no meaningful usage outside
   the Telegram ecosystem. This is structurally identical to BNB's dependency on
   Binance exchange volume, not merely a demand-side pull.

2. **Statistical home is the defensive/captive cluster.** TON's demeaned correlation
   to the defensive complex `{trx, ton, bnb, cro}` = 0.284; to
   `smart_contract_platform` members = 0.007.

3. **BTC beta is structurally compressed.** TON's ~0.89 BTC beta (2024+) fits the
   captive-franchise range (0.76–0.89 for BNB/CRO) and is far below the
   sovereign-L1 live-basket range (1.17–1.38). This compression reflects cash flows
   that persist when crypto risk appetite leaves.

4. **`established` test passes.** Telegram's franchise is not aspirational; TON has
   realized the largest per-user stablecoin-payments distribution of any chain outside
   TRON. This distinguishes TON from chains whose messenger/captive narratives have not
   reached realized flow.

## Cross-reference

See `decisions/sector-field-okx-2026-06.md` §Amendment 3 and `decisions/trx.md` for
the TRX precedent that the captive-franchise generalization builds on.
`validation/sector_okx/REPORT.md` §exception-register for quantitative detail.
