# Dissolve `ai_infrastructure` + `media_content` — narrative is not a mechanism

**Decision**: Remove the `ai_infrastructure` and `media_content` sector labels.
Redistribute all members by their underlying whitepaper/code mechanism. The flat
field goes from **15 → 13** sectors.

**Date**: 2026-06-20

## Principle

A sector must be defined by the token's **underlying mechanism** — what the
whitepaper and on-chain code actually implement — **not** by the application
narrative the project markets. "AI" is a narrative that cuts across sovereign L1
chains, GPU/compute DePINs, data networks, access tokens, and launchpads; it is
not itself a mechanism. Grouping tokens because the team "says AI" reproduces the
marketing, not the economics. (Codified as `taxonomy.yaml` precedence Rule 11.)

## Theory and data agreed

`ai_infrastructure` was empirically **RESIDUAL** with `mean_resid_corr = -0.002`
(negative/zero cohesion vs a 10k-perm null): the 18 "AI" coins did **not** co-move,
precisely because they were mechanically heterogeneous. The permutation test and the
first-principles mechanism reading reached the same conclusion — the bucket was not a
real group. `media_content` (n=3, `+0.005`, p≈0.32) failed the same cohesion bar.

`metaverse_gaming` is also use-case-flavoured but was **kept**: it passes the
empirical bar (FACTOR, `+0.04`, p=0.0001). The governing test is therefore
**mechanism-coherent definition AND empirical cohesion** — AI failed both,
media_content failed cohesion, gaming passes cohesion.

## Redistribution (23 coins, adversarially verified; 0 to OTHER)

| → destination | coins | mechanism |
|---|---|---|
| smart_contract_platform | 0G, KITE, TAO, THETA, VANA | sovereign L1s (AI is narrative; e.g. THETA EdgeCloud fees are TFUEL, not THETA) |
| compute_storage | RENDER, GLM, ATH, GRASS, LPT | paid-provider GPU/compute/bandwidth DePIN |
| information_technology | AIXBT, COAI, RECALL, SAHARA, SAPIEN, SHELL, BAT | access-gating to off-chain SaaS / data-service middleware |
| oracles_data | ALLO | appchain outputting only verified ML prediction feeds |
| captive_franchise | NMR, ME | single-operator off-chain revenue → buyback loop |
| defi | VIRTUAL | bonding-curve launchpad + DEX |
| meme | ZORA | live product but zero holder accrual ("for fun only") |

`BLUR` was confirmed in `defi` (NFT marketplace + Blend NFT-lending; fee-switch
unpassed is irrelevant to mechanism); `ME` moved `metaverse_gaming → captive_franchise`.

## Consequences (10k-perm re-validation)

- **`compute_storage`** widened from "burn/lock-for-resource" to "decentralized
  physical-resource marketplace/DePIN (GPU/compute, storage, bandwidth; paid-provider
  OR burn/lock)". Cohesion diluted **+0.18 (n=4) → +0.06 (n=9)** but remains a clear
  FACTOR — GPU and storage DePINs genuinely co-move.
- **`information_technology` reclassified FACTOR → RESIDUAL.** After absorbing the
  mechanism-correct access/data-service tokens its cohesion fell **+0.011 (n=22) →
  +0.004 (n=29)** — effect-size residual (like defi). It is now an explicit
  negative-space services bucket, pooled to OTHER in `group_neut`, and the leading
  candidate for the next mechanism-based re-audit.
- **`captive_franchise`** widened to single-operator fund/marketplace buyback loops
  (NMR, ME); cohesion **+0.30 (n=4) → +0.17 (n=6)**, still strong.
- `meme` definition clarified (admits live-product tokens with zero holder accrual);
  `oracles_data` clarified (verified-feed appchains belong here, not SCP).

Per-universe variance-reduction figures: `validation/sector_okx/REPORT.md`.

## Method

Two adversarial multi-agent passes (economics-first re-audit, then mechanism
redistribution): each placement was proposed by one agent and independently
stress-tested by a skeptic; not-yet-live mechanisms (e.g. Sahara Chain L1) were
barred from aspirational buckets. See `taxonomy.yaml` Rules 7, 9, 11 for the boundary
logic and `classification/sector.csv` `note` column for per-coin rationale.
