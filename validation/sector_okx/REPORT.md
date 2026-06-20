# Validation Report: flat `sector` field (v3, 232-coin OKX universe)

> Version: 3.0.0 · Date: 2026-06-20
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

A single flat `sector` field (15 labels, one layer, no hierarchy) over the 232-coin
OKX crypto-native perpetual universe is the recommended axis for `group_neut`-style
cross-sectional factor neutralization. Labels are economics-first (assignable from a
token's value-accrual mechanism, not its correlation matrix). Under the production
OTHER-collapse kernel, per-day cross-sectional variance reduction is **+4.69 pp above a
size-preserving permutation null on the full 232 universe (12.91% vs 8.22%, p = 0.0001,
10,000 draws)**, rising to **+6.75 pp on TOP30 (22.78% vs 16.03%, p = 0.0008)**. The
grouping is Holm-robust across four universes. Per-group cohesion is honest and uneven:
five labels carry a strong shared residual factor (privacy, captive_franchise,
value_transfer, compute_storage, meme), three are weak-but-significant, two are marginal
(significant only because large *n* tightens the null), and five — including the new
`ai_infrastructure` and `oracles_data` carve-outs — are statistically residual and are
pooled to OTHER in `group_neut`.

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
the null (demeaning is ≈ a no-op).

---

## 2. Variance reduction (10,000-perm, production kernel)

| Universe | n | min_assets | VR | null mean | **excess** | **p** | days |
|---|---|---|---|---|---|---|---|
| ALL | 232 | 30 | 12.91% | 8.22% | **+4.69 pp** | **0.0001** | 2,109 |
| TOP30 | 30 | 20 | 22.78% | 16.03% | **+6.75 pp** | **0.0008** | 1,138 |
| TOP50 | 50 | 30 | 17.97% | 11.50% | **+6.48 pp** | **0.0001** | 1,056 |
| TOP100 | 100 | 40 | 17.46% | 11.75% | **+5.71 pp** | **0.0001** | 1,120 |

Significant in all four universes. The TOP30 excess (+6.75 pp) reproduces the
independently-built robust-universe figure (+6.81 pp) to within Monte-Carlo error.
Raw outputs: `validation/sector_okx/varred_sector.json`, run log `run_10k.log`.

## 3. Per-group cohesion (10,000-perm)

| group | n | mean resid-corr | p | tier |
|---|---|---|---|---|
| privacy | 3 | +0.546 | 0.0001 | **FACTOR (strong)** |
| captive_franchise | 4 | +0.300 | 0.0001 | **FACTOR (strong)** |
| value_transfer | 7 | +0.228 | 0.0001 | **FACTOR (strong)** |
| compute_storage | 4 | +0.182 | 0.0001 | **FACTOR (strong)** |
| meme | 30 | +0.097 | 0.0001 | **FACTOR (strong)** |
| eth_scaling | 10 | +0.043 | 0.0018 | FACTOR (weak) |
| metaverse_gaming | 19 | +0.036 | 0.0001 | FACTOR (weak) |
| interoperability | 8 | +0.029 | 0.0173 | FACTOR (weak) |
| smart_contract_platform | 40 | +0.013 | 0.0001 | FACTOR (marginal) |
| information_technology | 22 | +0.011 | 0.0016 | FACTOR (marginal) |
| OTHER | 5 | +0.030 | 0.0717 | RESIDUAL |
| oracles_data | 8 | +0.008 | 0.1151 | RESIDUAL |
| media_content | 3 | +0.005 | 0.3207 | RESIDUAL |
| defi | 51 | +0.003 | 0.0001 | RESIDUAL |
| ai_infrastructure | 18 | −0.002 | 0.0846 | RESIDUAL |

Full table: `validation/sector_okx/cohesion_sector.csv`.

## 4. Honest limitations

- **`ai_infrastructure` and `oracles_data` are RESIDUAL.** They are economically real,
  newly carved-out organizational labels, but do **not** pass cohesion as standalone
  factors and are pooled to OTHER in `group_neut`. They are candidates for sub-division
  (defi → dex / lending / lsd / rwa / perps; ai → gpu-compute / agents / data) once each
  sub-leaf reaches ≥ 3 live members — not for use as factors today.
- **The big buckets are mostly market beta.** `smart_contract_platform`,
  `information_technology` and `defi` are statistically significant only because their
  large *n* tightens the null; their effect sizes (+0.01 to +0.003) are near zero. Most
  of their co-movement is market beta, not a sector factor.
- **`p`-value ≠ effect size.** For large groups, treat the cohesion magnitude, not the
  `p`-value, as the deployment signal.
- **Not a risk model.** This is a validated classification, an input to the industry
  block of a factor-risk exposure matrix — not a covariance forecast.
- **Survivorship / PIT.** Labels are time-invariant over each coin's traded history;
  `audit_from` records when a label was assigned (provenance), not a regime boundary.
  The universe is the set of currently-listed OKX perps (survivors).
