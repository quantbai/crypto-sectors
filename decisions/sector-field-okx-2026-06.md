# OKX-universe sector field — coin-by-coin economic audit (2026-06-14)

**Decision**: commit 16 sector reassignments to the 232-coin OKX deployment
universe (see `classification/sector.csv`), unify the GPU-compute
trio into `ai_infrastructure`, codify a 3-way `ai_infrastructure` boundary rule,
and add `cg_id` / `okx_instid` identity-anchor columns.

**Date**: 2026-06-14
**Supersedes for the OKX universe**: the Round-6 committed state (pre-audit).
Base decision record: `decisions/sector-field.md` (232-coin OKX perpetual universe).

---

## 1. Method

A multi-agent audit (workflow `wf_75f1d4d7-b7e`, 118 agents, ~4.4M subagent
tokens) reviewed all 232 coins under two lenses, then adversarially verified
every proposed change:

- **Lens 1 (per-coin)**: 12 batches × ~20 coins; each coin researched for its
  value-accrual mechanism and judged keep / move / uncertain.
- **Lens 2 (boundary)**: 6 auditors on the error-prone interfaces
  (defi↔SCP↔captive, IT↔ai_infrastructure↔oracles_data↔compute_storage,
  meme↔gaming↔media, currency↔privacy↔SCP, scaling↔interop↔SCP, OTHER).
- **Adversarial verification**: each of the 33 flagged coins got 3 skeptic
  votes (lenses: value-accrual, product cash-flow, project-liveness) defaulting
  to "keep current"; a move needed ≥2/3 to survive. **14 survived, 19 refuted.**

Mandate (unchanged): **economics only** — value-accrual mechanism from whitepaper
+ chain data; correlation / size / vol are never decision criteria; bias toward
keep; OTHER reserved for non-directional / dead assets.

The two remaining decisions (GPU trio, four split-vote boundary coins) were
referred to the maintainer, who chose: unify the GPU trio into
`ai_infrastructure`, and apply the recommended boundary calls.

## 2. Committed changes (16)

| Coin | From | To | Economic basis |
|---|---|---|---|
| IOTA | information_technology | smart_contract_platform | Post-Rebased (2025-05) sovereign MoveVM L1 (own Mysticeti dPoS, gas fee-burn + staking); IoT-middleware mechanism retired. **Stale-data fix.** |
| SOON | interoperability | eth_scaling | SOON Mainnet is an SVM rollup settling to Ethereum (EigenDA/Avail); $SOON is its gas/staking. InterSOON messaging is secondary. |
| ZORA | metaverse_gaming | media_content | Onchain social/content rail (posts → tradeable creator coins; ZORA = mint-fee + liquidity-pair currency). No games/virtual worlds. |
| VIRTUAL | information_technology | ai_infrastructure | AI-agent launchpad/marketplace; agent-creation + 1% trade tax + inference fees → buyback/burn. Child agent AIXBT already ai_infra. |
| KITE | information_technology | ai_infrastructure | Sovereign L1 for autonomous AI-agent payments; per-tx AI-service commission → KITE buy pressure. Metered AI-agent execution. |
| SAHARA | information_technology | ai_infrastructure | Live driver = metered AI data/model/inference marketplace (Sahara Chain not yet live). function_beats_chain. *(maintainer call)* |
| ATH | information_technology | ai_infrastructure | Aethir AI-focused GPU-as-a-service (H100/Blackwell, ~70% AI inference). *(GPU trio)* |
| RENDER | information_technology | ai_infrastructure | Decentralized GPU render/compute marketplace. *(GPU trio — unified, not workload-split)* |
| GLM | information_technology | ai_infrastructure | Golem decentralized GPU/compute marketplace. *(GPU trio)* |
| MAGIC | ai_infrastructure | metaverse_gaming | Treasure DAO cross-game currency since 2021; AI agents are gameplay features, not metered AI. |
| KGEN | ai_infrastructure | metaverse_gaming | Meters verified-gamer distribution / user-acquisition sold to publishers; AI is a downstream data buyer. |
| WLD | ai_infrastructure | information_technology | Value = World ID proof-of-personhood verification fees; no metered AI (AI is narrative). Identity middleware → IT. |
| PIEVERSE | ai_infrastructure | information_technology | Agentic payment/neobank stack (x402b, pieUSD); AI is UX, not metered AI → payment middleware residual. *(maintainer call)* |
| DOOD | meme | metaverse_gaming | Doodles NFT/entertainment IP brand with a live product (WLFI precedent: a product disqualifies meme). *(maintainer call)* |
| HMSTR | metaverse_gaming | meme | Telegram tap-to-earn; 60–75% airdropped, no fee/burn/paid-game economy; attention-driven (NOT/PENGU peer). |
| ACH | OTHER | information_technology | Alchemy Pay is a LIVE fiat-crypto payment rail (173 countries, fee/staking/buyback) — not a zombie. Open payment middleware → IT. *(maintainer call)* |

### Validation
Post-audit VR (production OTHER-collapse kernel, min30, full 232-coin OKX panel):
**16.38%** (perm null 10.53%, p=0.0033), vs pre-audit 16.84% (null 10.46%,
p=0.0033). The −0.46pp is the expected cost of **economics-first** reclassification
(moves were not chosen to raise VR); significance is unchanged. The largest VR
cost is broadening `ai_infrastructure` to 16 members incl. the GPU trio (lower
internal cohesion than a tight AI-agent cluster) — an accepted trade for
economic coherence and theme co-movement.

## 3. Systemic findings

1. **`ai_infrastructure` 3-way boundary rule** (codified in `taxonomy.yaml`
   `sector_field.okx_universe_amendments`): IN when token value IS metered AI;
   OUT to functional home when AI is a client vertical / downstream buyer; OUT to
   IT when AI is narrative-only. 8 of 14 moves touched this bucket.
2. **GPU-compute marketplaces unified** (ath/render/glm): economic twins with an
   identical token mechanism (pay-for-GPU, payment transferred to providers, so
   NOT compute_storage). Unify rather than split by workload-mix.
3. **Ticker-collision = data-integrity risk**: two refuted moves (EDEN, OL) were
   driven by reviewers researching the wrong project. Fixed by adding `cg_id` and
   `okx_instid` identity-anchor columns; resolve by slug, never ticker.
   Verified anchors: `eden = openeden-eden`, `ol = openloot`.

No sector needed splitting or merging; the meme↔gaming and IT-residual
boundaries held against bad carve attempts (ENSO, SSV, GLM-as-storage, RENDER,
NOT, PENGU, FLOKI, ZEN, BABY, ZETA, INIT, LAYER, PARTI, ONE, LUNA, LRC).

## 4. Artifacts & reproducibility

The authoritative published output of this audit is `classification/sector.csv`.
The internal derivation scripts and intermediate files used during the audit are
not part of the public repo; the CSV is the source of truth for downstream use.

- `classification/sector.csv` — current labels with `audit_from`, `cg_id`,
  `okx_instid` columns (published source of truth).

*(Internal note: the derivation pipeline — `build_final_sector.py`, the delta
script `apply_audit_2026-06-14.py`, the full audit report
`sector_review_2026-06-14.md`, structured changes `sector_review_changes.json`,
and post-audit VR file `okx_sector_final_validation.json` — lives in the
maintainer's private working directory and is not distributed with the repo.)*

## 5. Open items

- `cg_id` coverage is 119/232 (from the maintainer corpus + verified overrides);
  full backfill is deferred to the static-universe (TOP-N) step, which also needs
  market cap for the remaining ~113 coins.
- Canonical merge (whether the OKX universe replaces any prior
  `classification/` artefacts + full `taxonomy.yaml` sector_field) remains a
  separate, un-taken decision.
