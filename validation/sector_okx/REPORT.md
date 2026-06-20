# Validation Report: flat `sector` field (232-coin OKX universe)

> Date: 2026-06-20
> 232 crypto-native coins (OKX USDT-margined perpetuals)
> Daily log-returns 2019-11-27 → 2026-06-13 (2,391 days)
> Reproduce: `python scripts/validate_sector_okx.py --n-perm 10000`

**Status**: validated for research and `group_neut`-style cross-sectional factor
neutralization. Alpha-capital deployment remains paper-trading-gated (no
market-cap-weighted historical replication in repo). This is a validated
**classification** — an input to a risk model's exposure matrix — **not** a
covariance/factor risk model.

---

## Abstract

A single flat `sector` field (13 labels, one layer, no hierarchy) over the 232-coin
OKX crypto-native perpetual universe is the recommended axis for `group_neut`-style
cross-sectional factor neutralization. Labels are economics-first — assignable from a
token's underlying value-accrual **mechanism** (whitepaper + on-chain code), not its
correlation matrix and not the application narrative the project markets. Under the
production OTHER-collapse kernel, per-day cross-sectional variance reduction is
**+5.03 pp above a size-preserving permutation null on the full 232 universe (12.73% vs
7.69%, p = 0.0001, 10,000 draws)**, rising to **+6.75 pp on TOP30 (22.78% vs 16.03%,
p = 0.0008)**. The grouping is robust across four universes (all p ≤ 0.0008). Per-group
cohesion is honest and uneven: three labels carry a strong shared residual factor
(privacy, value_transfer, captive_franchise), two are moderate (meme, compute_storage),
three are weak-but-significant, one is marginal, and four are statistically residual and
pooled to OTHER in `group_neut`.

This run reflects the 2026-06-20 dissolution of the `ai_infrastructure` and
`media_content` labels (narrative buckets with ~zero cohesion), whose members were
redistributed by mechanism, and the reclassification of `information_technology` to
RESIDUAL. See `decisions/dissolve-ai-narrative.md`.

---

## 1. Methodology

### 1.1 Production kernel (OTHER-collapse)

This is exactly what `group_neut` does, and what the variance-reduction numbers measure.
For each day *t*:

1. Demean returns **within each FACTOR sector** that has ≥ 3 live (non-NaN) members.
2. Pool **RESIDUAL-labelled coins** — and any sub-3-member FACTOR group on that day —
   into **OTHER**, then demean the OTHER pool (market-neutralize it).

This is deliberately conservative. A naive "demean within every label" kernel overstates
variance reduction by crediting tiny residual groups; the OTHER-collapse kernel does not.

### 1.2 Variance reduction & null

- **VR(t)** = `1 − var(resid_t) / var(ret_t)`, averaged over days with ≥ `min_assets`
  valid coins (the deployment-relevant threshold).
- **Null**: group-size-preserving label shuffle (10,000 draws, seed 42). The label
  vector is permuted across coins, preserving each group's size; `p` = fraction of null
  draws ≥ observed.

### 1.3 Cohesion (FACTOR vs RESIDUAL)

Per group, the mean intra-group pairwise correlation of **market-residual** returns
(each day's cross-section demeaned by its mean) over pairs with ≥ 180 overlapping days,
vs a label-shuffle null. A label is FACTOR if within-group demeaning removes a shared
post-market factor; RESIDUAL if its intra-group correlation is indistinguishable from
the null (demeaning is ≈ a no-op). **FACTOR/RESIDUAL is decided by EFFECT SIZE, not
`p`-value**: a large bucket can be p-significant with ~zero effect (defi and
information_technology are p < 0.01 but RESIDUAL by effect size).

---

## 2. Variance reduction (10,000-perm, production kernel)

| Universe | n | min_assets | VR | null mean | **excess** | **p** | days |
|---|---|---|---|---|---|---|---|
| ALL | 232 | 30 | 12.73% | 7.69% | **+5.03 pp** | **0.0001** | 2,109 |
| TOP30 | 30 | 20 | 22.78% | 16.03% | **+6.75 pp** | **0.0008** | 1,138 |
| TOP50 | 50 | 30 | 19.06% | 12.82% | **+6.23 pp** | **0.0001** | 1,056 |
| TOP100 | 100 | 40 | 17.18% | 11.24% | **+5.94 pp** | **0.0001** | 1,120 |

Significant in all four universes. Dissolving the two zero-cohesion narrative buckets and
pooling the now-RESIDUAL `information_technology` (29 coins) into OTHER **improved** the
honest excess at ALL (+4.69 → +5.03 pp) and TOP100 (+5.71 → +5.94 pp), left TOP30 unchanged
(its members are all outside the relabelled set), and cost ~0.25 pp at TOP50 — demeaning
within a non-cohesive group adds noise; pooling it into the market-neutral OTHER is cleaner.
Raw outputs: `validation/sector_okx/varred_sector.json`, run log `run_10k.log`.

## 3. Per-group cohesion (10,000-perm)

| group | n | mean resid-corr | p | tier |
|---|---|---|---|---|
| privacy | 3 | +0.546 | 0.0001 | **FACTOR (strong)** |
| value_transfer | 7 | +0.228 | 0.0001 | **FACTOR (strong)** |
| captive_franchise | 6 | +0.171 | 0.0001 | **FACTOR (strong)** |
| meme | 31 | +0.091 | 0.0001 | **FACTOR (moderate)** |
| compute_storage | 9 | +0.060 | 0.0009 | **FACTOR (moderate)** |
| eth_scaling | 10 | +0.043 | 0.0018 | FACTOR (weak) |
| metaverse_gaming | 18 | +0.038 | 0.0001 | FACTOR (weak) |
| interoperability | 8 | +0.029 | 0.0173 | FACTOR (weak) |
| smart_contract_platform | 45 | +0.010 | 0.0001 | FACTOR (marginal) |
| information_technology | 29 | +0.004 | 0.0026 | RESIDUAL |
| defi | 52 | +0.002 | 0.0001 | RESIDUAL |
| oracles_data | 9 | −0.001 | 0.1939 | RESIDUAL |
| OTHER | 5 | +0.030 | 0.0717 | RESIDUAL (by design) |

Full table: `validation/sector_okx/cohesion_sector.csv`.

## 4. Honest limitations

- **`information_technology` is RESIDUAL.** After the `ai_infrastructure` dissolution
  placed the mechanism-correct access / data-service tokens here, its cohesion fell to
  +0.004 (n=29) — effect-size residual, like defi. It is an explicit negative-space
  services bucket, pooled to OTHER in `group_neut`, and the leading candidate for the
  next mechanism-based re-audit (or sub-division once ≥3-member coherent sub-leaves emerge).
- **`compute_storage` was widened** to include paid-provider GPU / compute / bandwidth
  DePINs (render / glm / ath / grass / lpt). Cohesion diluted from +0.18 (n=4) to +0.06
  (n=9) but remains a clear FACTOR — GPU and storage DePINs genuinely co-move.
- **The big buckets are mostly market beta.** `smart_contract_platform` (+0.010),
  `information_technology` (+0.004) and `defi` (+0.002) are statistically significant only
  because their large *n* tightens the null; their effect sizes are near zero.
- **`p`-value ≠ effect size.** For large groups, treat the cohesion magnitude, not the
  `p`-value, as the deployment signal.
- **Not a risk model.** This is a validated classification, an input to the industry block
  of a factor-risk exposure matrix — not a covariance forecast.
- **Survivorship / PIT.** Labels are time-invariant over each coin's traded history;
  `audit_from` records when a label was assigned (provenance), not a regime boundary. The
  universe is the set of currently-listed OKX perps (survivors).
