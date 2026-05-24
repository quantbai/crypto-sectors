# PRIME — Echelon Prime reclassification

**asset_id**: `prime`
**Symbol**: PRIME
**Decision**: reclassify from `301092` (RWA Issuer — Governance, sector 3010 DeFi) to `305020` (Gaming, sector 3050 Metaverse)
**Effective from**: `2024-05-23` (v1.0.0-RC2)
**Date of this decision**: 2026-05-24
**Related issue / PR**: internal — v1.0 upgrade plan §2 D3

---

## What Echelon Prime actually does

Echelon Prime is the economic infrastructure layer for blockchain-native games, with Parallel TCG (a sci-fi trading card game) as its primary live product. PRIME token serves as the in-game currency and governance token for the Echelon ecosystem: it is used to earn rewards through gameplay, stake for protocol fees, and vote on ecosystem treasury allocations. The protocol's revenue derives from gaming activity — card packs, tournament fees, and in-game item transactions — not from real-world asset (RWA) issuance or treasury management. Echelon has no fiat reserves, no tokenized securities exposure, and no treasury-bill backing. It is a gaming-economy token.

---

## Why 305020 (Gaming) and not 305010 (Virtual Worlds)

The taxonomy defines these two sub-sectors as follows:

> **305010 — Virtual Worlds**: Tokens native to applications facilitating transfer of digital land and metaverse interaction.

> **305020 — Gaming**: Tokens native to blockchain games and gaming communities.

PRIME is the token of a blockchain game (Parallel TCG) and its surrounding gaming economy (Echelon). It is not a land-transfer or metaverse-interaction token. The distinction is economic function:

- **305010** captures assets whose value derives from virtual real-estate scarcity, metaverse platform transactions, and land-plot economics (e.g. SAND, MANA — The Sandbox and Decentraland).
- **305020** captures assets whose value derives from gameplay activity, in-game rewards, and tournament economics — a game-revenue model, not a land-scarcity model.

Parallel TCG has cards, not parcels. Its value accrues through active gameplay and card-pack sales, not land appreciation. Echelon's documentation is explicit: PRIME is the "fuel" of gameplay loops. Assignment to 305020 is unambiguous.

---

## Why 301092 (RWA Issuer — Governance) was wrong

`301092` is defined as:

> **301092 — RWA Issuer — Governance** [EXT]: Governance tokens of protocols that tokenize real-world assets (treasuries, credit, equities). Distinct from the RWA tokens themselves, which live in 402010.

Echelon Prime has no real-world asset backing, no fiat-reserve exposure, no treasury-bill or credit portfolio. The original classification appears to have been an error of category — possibly a confusion with another `30xx` sub-sector in the DeFi family. PRIME has no economic relationship with RWA tokenization. The correct assignment requires looking at fee flow: where does the value that accrues to PRIME token come from? The answer is gaming transactions, not RWA management fees. `301092` was incorrect from v1.0-RC1.

---

## Alternatives considered

| Alternative | Code | Rejected because |
|---|---|---|
| Virtual Worlds | 305010 | PRIME is a gaming token, not a virtual-land token. No land-parcel mechanics. |
| RWA Issuer — Governance | 301092 | No RWA exposure. Original misclassification. |
| Metaverse (sector 3050, unspecified) | — | All three sub-sectors evaluated; 305020 is the correct leaf. |
| Meme Coins | 102010 | PRIME has substantive protocol utility; it is not primarily a social-narrative token. |
