# sector — master memo

**Decision**: adopt a single flat `sector` field (15 labels, no hierarchy) on the
232-coin OKX USDT-margined perpetual universe as the primary axis for
`group_neut`-style cross-sectional factor neutralization.

**Date**: 2026-06-20  
**Audit record** (coin-by-coin): `decisions/sector-field-okx-2026-06.md`

---

## 1. The decision

The product is a single flat `sector` field, 15 labels, anchored to the 232-coin OKX
perpetual universe, empirically validated for `group_neut`.

**Why flat?**  
Cross-sectional neutralization (`group_neut`) requires one label per coin per day.
A hierarchy is a distraction: the group you demean within is always a leaf. Making that
leaf explicit, validated, and documented is strictly better than picking the "right
level" of a hierarchy at call time. Fifteen labels is the right granularity — small
enough that every group has sufficient live members for a meaningful within-group demean,
large enough to capture the distinct economic clusters that exist in the data.

**Why 232-coin OKX perpetuals?**  
This is the production trading universe (OKX USDT-margined perps, daily log-returns
2019-11-27 → 2026-06-13, 2391 rows). Identity is anchored by `cg_id`
(CoinGecko slug) + `okx_instid` to avoid ticker-collision mis-resolution.
Classifications validated on a smaller sub-universe are not production-ready for this
universe.

---

## 2. Economics-first design philosophy

**A label must be answerable from the token's economic design, not its correlation
matrix.**

The guiding rule: can you assign the label by reading the whitepaper and on-chain
mechanics, without looking at returns? If yes, the label is valid. If the only
justification is "it correlates with group X", the placement is rejected.

This constraint is not cosmetic. It is what makes the classification transferable:
a new coin can be labeled before it has a price history. It is also what keeps the
product honest — correlation-led groupings overfit the historical window.

Concretely:
- Precedence rules are economics-first (defined in `taxonomy.yaml`).
- Statistical evidence (pairwise demeaned correlation, bootstrap cluster frequency,
  variance-reduction contribution) is used to **confirm** groups and **adjudicate**
  boundary cases. It never **defines** a group.
- Vintage (listing year, "old-guard") is explicitly forbidden as a criterion. Listing
  year is not token economics.
- Size is explicitly forbidden. ETH is not a separate group because it is large.

Per-coin economic rationale is recorded in `research/` (128 notes) and non-trivial
boundary decisions are recorded in `decisions/`.

---

## 3. The 15 sector labels

Labels, their economic definitions, and governance role (FACTOR vs RESIDUAL) are
canonical in `taxonomy.yaml`. Brief summary:

| sector | economic logic |
|---|---|
| `privacy` | cryptographic privacy as a primary protocol feature (shielded pools, opt-in mixing) |
| `captive_franchise` | quasi-equity of an established captive distribution franchise monetized via fee/burn |
| `value_transfer` | payment-optimized L1s where the primary utility is peer-to-peer value transfer |
| `compute_storage` | tokens metering decentralized compute/storage; payment burned/locked for resource usage |
| `meme` | zero cash-flow, zero utility claim; value is purely social/speculative |
| `eth_scaling` | rollups and validiums that settle to Ethereum for security (fee revenue inherits from ETH) |
| `metaverse_gaming` | in-game economies and virtual-world ownership primitives |
| `interoperability` | cross-chain messaging and bridge security tokens |
| `smart_contract_platform` | general-purpose programmable L1s (not payment-primary) |
| `information_technology` | infrastructure middleware: oracles, naming, wallets, identity, developer tooling |
| `defi` | on-chain financial intermediation: DEX/AMM, lending, LSD, RWA, perps |
| `ai_infrastructure` | AI-specific protocol infrastructure: GPU compute networks, on-chain AI agents |
| `oracles_data` | dedicated data-feed and oracle networks (carved out of IT for organizational clarity) |
| `media_content` | content monetization, creator economies, streaming |
| `OTHER` | not a label in `sector.csv`; a runtime concept — see §4 |

---

## 4. Production OTHER-collapse kernel

This is what `group_neut` does, and what the validation measures.

**Per day:**

1. For each FACTOR sector with **≥ 3 live members** that day: demean returns within
   the group (subtract the equal-weighted group mean).
2. Pool all RESIDUAL-labelled coins **plus** any FACTOR group that fell below 3 live
   members into a single **OTHER** pool.
3. Demean returns within the OTHER pool (market-neutralize the residual).

The OTHER-collapse kernel is the **conservative / honest** kernel. A naive kernel that
demeaned within every label regardless of membership would produce inflated variance
reduction numbers, because small random groups can appear cohesive by chance. The
10k-perm null is calibrated to this same kernel, so the published VR numbers are
apples-to-apples.

`OTHER` is a runtime concept, not a label. `sector.csv` never contains `OTHER`.

---

## 5. Validation results (10,000-perm, production kernel)

Metric: per-day cross-sectional variance reduction (VR) vs a size-preserving
label-shuffle null, averaged over days with ≥ `min_assets` valid coins.

| Universe slice | n coins | min_assets | VR | null mean | excess | p |
|---|---|---|---|---|---|---|
| ALL | 232 | 30 | 12.91% | 8.22% | +4.69 pp | 0.0001 |
| TOP30 | 30 | 20 | 22.78% | 16.03% | +6.75 pp | 0.0008 |
| TOP50 | 50 | 30 | 17.97% | 11.50% | +6.48 pp | 0.0001 |
| TOP100 | 100 | 40 | 17.46% | 11.75% | +5.71 pp | 0.0001 |

All four slices are Holm-significant. Full details: `validation/sector_okx/REPORT.md`.
Artefacts: `validation/sector_okx/varred_sector.json`, `cohesion_sector.csv`,
`run_10k.log`.

The size-preserving null is not a weak baseline. It controls for the trivial effect
that demeaning within large groups absorbs more variance. It can reject: a
correlation-maximalist statistical design that naively chased VR failed the TOP30
permutation test (observed < null mean, p = 0.62) during the design selection phase.

---

## 6. FACTOR / RESIDUAL governance with STRONG / WEAK / MARGINAL tiers

Source: `validation/sector_okx/cohesion_sector.csv` (mean intra-group
market-residual pairwise correlation, 10k-perm). These numbers govern behavior in the
production kernel (FACTOR groups demean within-group; RESIDUAL groups pool to OTHER).

**FACTOR — STRONG** (clear within-group return factor):

| sector | mean resid corr |
|---|---|
| `privacy` | +0.55 |
| `captive_franchise` | +0.30 |
| `value_transfer` | +0.23 |
| `compute_storage` | +0.18 |
| `meme` | +0.10 |

**FACTOR — WEAK** (significant vs null but modest effect; within-group demean is
beneficial, not transformative):

| sector | mean resid corr |
|---|---|
| `eth_scaling` | +0.04 |
| `metaverse_gaming` | +0.04 |
| `interoperability` | +0.03 |

**FACTOR — MARGINAL** (statistically significant only because large n tightens the
permutation null; cohesion is weak; demean is mostly removing market beta):

| sector | mean resid corr |
|---|---|
| `smart_contract_platform` | +0.013 |
| `information_technology` | +0.011 |

Marginal FACTOR sectors are still included in the within-group demean (they beat
the null) but should be treated with caution. A within-group demean on a low-cohesion
group mostly market-neutralizes, not sector-neutralizes.

**RESIDUAL** (intra-group correlation indistinguishable from null; within-group demean
is ~a no-op; pooled to OTHER in production kernel):

| sector | mean resid corr |
|---|---|
| `defi` | +0.003 |
| `ai_infrastructure` | −0.002 |
| `oracles_data` | +0.008 |
| `media_content` | +0.005 |

RESIDUAL labels are kept as **organizational labels** — they inform coin lookup,
research, and future sub-division — but contribute no neutralization beyond the
pooled OTHER demean.

The `role` field in `classification/sector.csv` and `classification/sector_roles.json`
encodes FACTOR vs RESIDUAL for each label.

---

## 7. Limitations (disclosed honestly)

**`ai_infrastructure` and `oracles_data` are RESIDUAL.**  
These are new carve-outs from `information_technology`. They do not pass the cohesion
test as currently constituted. They are kept as organizational labels and candidates
for sub-division once each sub-leaf has ≥ 3 live members (e.g., defi →
dex/lending/lsd/rwa/perps; ai → gpu-compute/agents/data-infra). Do not treat them as
neutralization groups.

**The big buckets are mostly market beta.**  
`smart_contract_platform` (mean resid corr +0.013), `information_technology`
(+0.011), and `defi` (+0.003) are large groups where statistical significance comes
from n, not from cohesion. A within-group demean on these groups is predominantly
market-neutralization wearing a sector label. This is not wrong — market-neutralization
is useful — but the user should not expect strong idiosyncratic factor removal from
these groups the way they should expect it from `privacy` or `captive_franchise`.

**This is NOT a risk model.**  
`sector` is a validated classification — an input to a risk model's exposure matrix.
It is not a covariance matrix, a factor risk model, or a returns model. Never describe
it as a "risk model."

**Deployment gate.**  
The field is validated for research and group-neutralization. Alpha-capital deployment
is paper-trading-gated. No live capital should be committed to a strategy whose
only validation is the variance-reduction metric above.

**Selection bias.**  
Design selection and validation used the same panel (232 coins, 2019–2026). This
creates in-sample selection bias. Mitigations: (a) economics-first definitions are
recorded before validation runs; (b) ALL, TOP30, TOP50, TOP100 all independently clear
the 10k-perm null; (c) future quarterly refreshes will accumulate genuinely held-out
forward data.

---

## 8. Published files

| file | description |
|---|---|
| `classification/sector.csv` | committed source of truth; 232 rows; columns: symbol, sector, role, cg_id, okx_instid, audit_from, prev_label, note |
| `classification/sector.parquet` | parquet mirror (derived by `scripts/build_sector_field.py`) |
| `classification/sector_panel.parquet` | PIT (date × symbol) label matrix, pandas StringDtype, `<NA>` before listing; the `group_neut` input |
| `classification/sector_roles.json` | label → {role, n, mean_resid_corr, cohesion_p} |
| `classification/universe_tiers.json` | TOP10/20/30/50/100 membership lists |
| `data/returns.parquet` | 232-symbol daily log-returns |
| `taxonomy.yaml` | flat sector label definitions (economics-first), precedence/boundary rules, FACTOR/RESIDUAL governance note |
| `validation/sector_okx/` | varred_sector.json, cohesion_sector.csv, run_10k.log, REPORT.md |
| `decisions/sector-field-okx-2026-06.md` | coin-by-coin audit record |
| `research/` | 128 per-coin economic-rationale notes |

---

## 9. Reproduce

```
python scripts/build_sector_field.py                   # derive parquet + panel + roles from sector.csv
python scripts/validate_sector_okx.py --n-perm 10000  # full validation (~1.5 h); --n-perm 200 for smoke
python scripts/validate_schema.py                      # referential integrity
```

CI runs build + schema-validate + smoke-validate on every push (`.github/workflows/ci.yml`).

---

## 10. Cross-references

- `decisions/sector-field-okx-2026-06.md` — coin-by-coin audit record (the source of placement rationale)
- `taxonomy.yaml` — canonical label definitions and precedence rules
- `decisions/pol.md` — POL → `smart_contract_platform` (not `eth_scaling`); settlement-dependence rule
- `decisions/README.md` — index of all per-coin decision records
