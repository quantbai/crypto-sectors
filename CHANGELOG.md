# Changelog

All notable changes to crypto-sectors are documented here.

Format: `[vX.Y.Z] YYYY-MM-DD — N assets — Summary`.

---

## [v3.0.0] — 2026-06-20 — 232 assets — Pivot to single flat `sector` field on OKX 232-coin perp universe

### Breaking pivot: discard v2 4-tier MSCI hierarchy and 135-asset Section-4 universe

The product is now a **single flat `sector` field** for the 232-coin OKX USDT-margined perpetual
universe (daily log-returns 2019-11-27 to 2026-06-13, 2391 rows). The prior v2 product — a
4-tier MSCI-style hierarchy (`class_code`, `sector_code`, `sub_sector_code`, `chain_ecosystem`)
on a 135-asset universe and its associated Section-4 validation — is **discarded in its entirety**.

#### The field

15 flat sector labels (one layer, no hierarchy, no numeric codes). Identity-anchored by `cg_id`
(CoinGecko slug) + `okx_instid` to avoid ticker-collision mis-resolution.

**FACTOR sectors** (within-group demean removes a real shared return factor):
- Strong: `privacy` (+0.55), `captive_franchise` (+0.30), `value_transfer` (+0.23),
  `compute_storage` (+0.18), `meme` (+0.10)
- Weak but significant: `eth_scaling` (+0.04), `metaverse_gaming` (+0.04),
  `interoperability` (+0.03)
- Marginal (significant because large n tightens the null; mostly market beta — treat with
  caution): `smart_contract_platform` (+0.013), `information_technology` (+0.011)

**RESIDUAL sectors** (intra-group corr indistinguishable from null; pooled to OTHER in
`group_neut`): `defi` (+0.003), `ai_infrastructure` (-0.002), `oracles_data` (+0.008),
`media_content` (+0.005), OTHER.

(Numbers = mean intra-group market-residual pairwise correlation, 10k-perm;
see `validation/sector_okx/cohesion_sector.csv`.)

#### Production kernel

Per day: demean returns within each FACTOR sector with >=3 live members; pool RESIDUAL-labelled
coins AND any sub-3-member FACTOR group into OTHER, then demean that OTHER pool
(market-neutralize). This OTHER-collapse kernel is the conservative/honest kernel; a naive
"demean within every label" overstates VR.

#### Validation (10,000-perm, production OTHER-collapse kernel)

Per-day cross-sectional variance reduction vs a size-preserving label-shuffle null, averaged
over days with >= min_assets valid coins:

| Universe | min_assets | VR     | Null   | Excess   | p      |
|----------|-----------|--------|--------|----------|--------|
| ALL (232)| 30        | 12.91% | 8.22%  | +4.69pp  | 0.0001 |
| TOP30    | 20        | 22.78% | 16.03% | +6.75pp  | 0.0008 |
| TOP50    | 30        | 17.97% | 11.50% | +6.48pp  | 0.0001 |
| TOP100   | 40        | 17.46% | 11.75% | +5.71pp  | 0.0001 |

**Status**: validated for research and group-neutralization use; alpha-capital deployment
remains paper-trading-gated.

#### Honesty notes

- `ai_infrastructure` and `oracles_data` are NEW carve-outs that are **RESIDUAL** — they do
  not pass cohesion alone. Kept as organizational labels, pooled in `group_neut`; candidates
  for sub-division once each sub-leaf has >=3 live members.
- The big buckets (`smart_contract_platform`, `information_technology`, `defi`) are mostly
  market beta; their statistical significance comes from large n, not strong cohesion.
- NOT A RISK MODEL: this is a validated classification (an input to a risk model's exposure
  matrix), not a covariance/factor risk model.

#### New published files

- `classification/sector.csv` — committed source of truth; columns: symbol, sector, role,
  cg_id, okx_instid, audit_from, prev_label, note (232 rows)
- `classification/sector.parquet` — parquet mirror (derived by `build_sector_field.py`)
- `classification/sector_panel.parquet` — PIT (date x symbol) label matrix, pandas
  StringDtype, `<NA>` before listing; the `group_neut` input
- `classification/sector_roles.json` — label -> {role, n, mean_resid_corr, cohesion_p}
- `classification/universe_tiers.json` — TOP10/20/30/50/100 membership lists
- `data/returns.parquet` — 232-symbol daily log-returns (replaces `data/daily_returns.parquet`)
- `taxonomy.yaml` — flat sector label definitions (economics-first), precedence/boundary
  rules, FACTOR/RESIDUAL governance note; no 4-tier hierarchy
- `decisions/sector-field.md` — master memo (v3 pivot rationale)
- `decisions/sector-field-okx-2026-06.md` — audit record
- `research/` — 128 per-coin economic-rationale notes
- `validation/sector_okx/` — varred_sector.json, cohesion_sector.csv, run_10k.log, REPORT.md
- `scripts/` — build_sector_field.py, validate_sector_okx.py, validate_schema.py
- `.github/workflows/ci.yml` — CI: build + schema-validate + smoke-validate on published files

#### Removed / discarded files

All v2 artifacts are removed: `class_code`, `sector_code`, `sub_sector_code`,
`chain_ecosystem` hierarchy fields; `classification/snapshot.csv`; `classification/wide/*`;
`classification/long/*`; `data/daily_returns.parquet`; `validation/section4/`;
scripts `build_matrices.py`, `validate_paper_section4.py`,
`validate_section4_robustness.py`, `validate_universe_variants.py`,
`validate_extra_group_fields.py`, `build_group_fields.py`, `ols_groundtruth.py`,
`rerun_43_pit.py`, `validate_sector_field.py`, `audit_universe.py`;
`vol_bucket`, `beta_bucket`, `age_bucket` fields; `CONTRIBUTING.md`, `DESIGN.md`,
`GOVERNANCE.md`, `UNIVERSE.md`, `docs/`.

---

> The entries below predate the v3.0.0 pivot and describe the discarded 4-tier / 135-asset product. Their file paths, field names, and numbers (e.g. 44.07%) are historical and no longer apply to the current product.

## [v2.1.0-dev] — In development

### sector field: single recommended group axis for cross-sectional factor neutralization (2026-06-10)

New flat `sector` field — 13 directional labels on 133 directional assets (+1
non-directional `onchain_derivatives` bucket, universe-gated to `<NA>` in the wide
matrix). Validated at 23.45% per-day variance reduction (min_assets=30, 10,000-perm
confirmatory run complete at the 10,000-perm standard, p=0.0001 / p_holm=0.0004,
p_holm=0.002) vs 15.68% `sector_code` / 16.94% `chain_ecosystem` published baselines.
4 distinct universes (ALL / TOP30 / TOP50 / TOP100); TOP50 ≡ PIT-strict by construction
(same 50 assets). TOP30: 44.07% (p_holm 0.003), TOP50: 31.43% (p_holm 0.002),
TOP100: 24.83% (p_holm 0.002) — Holm-significant in all four universes (m=4).
Selected by a 3-designer / 3-judge panel from three candidate designs; the statistical
design rejected (TOP30 p=0.62, same sub_sector failure mode).

**Status**: validated for research and group-neutralization use; alpha-capital
deployment remains paper-trading-gated pending market-cap-weighted replication
(no historical supply data in repo yet) — same gate as the published Section-4 fields.

- `classification/snapshot.csv`: new `sector` column
- `classification/wide/sector.parquet` + `sector.csv`: new (date × asset_id) matrix;
  pandas StringDtype (not object); paxg/gas columns all-`<NA>` (class-40 universe gate)
- `classification/long/panel.parquet` + `panel.csv`: `sector` field added to long panel
- `taxonomy.yaml`: `sector_field:` section with 14 enumerated labels + `crosswalk:`
  reconciliation table; version bumped to 2.1.0-dev
- `SCHEMA.md`: `sector` field documented with StringDtype, three NaN causes, class-40
  gate, consumer contract (per-day min-group collapse), and CI checks 14-17
- `scripts/validate_schema.py`: checks 14-17 added (StringDtype, column set, class-40
  gate, no label drift, ≥3 live members per directional label from 2024-01-01)
- `scripts/build_matrices.py`: universe-gates class-40 assets (paxg/gas) to `<NA>` in
  `classification/wide/sector.parquet`; casts sector label matrices to pandas StringDtype
- `scripts/validate_sector_field.py`: standalone validation script for the `sector` field
- `validation/sector_field/REPORT.md`: full validation report
- `decisions/sector-field.md`: master memo — design provenance, panel decision, amendments,
  refused moves, selection-bias note (9-design search; selection premium ≈ 2pp)
- `decisions/pol.md`: appended Amendment 1 (POL → `smart_contract_platform`) + axis
  reconciliation paragraph
- `decisions/dcr.md`: new — DCR → `privacy` (opt-in StakeShuffle; regulatory tail-risk
  deciding argument; bootstrap 0.99 corroborating)
- `decisions/ton.md`: new — TON → `captive_franchise`
- `decisions/twt.md`: new — TWT → `captive_franchise`
- `decisions/wal.md`: new — WAL → `compute_storage`
- `decisions/trx.md`: appended sector-field placement (`tron_ecosystem`) cross-reference

---

## [v2.0.0] — In development

Initial public release. Pre-v2 development history (taxonomy iteration, universe lockdown, returns-data backfill, empirical-validation rewrite) is consolidated into this release and not separately versioned.

### Section 4 statistical rework (2026-05-27, post AQR P0/P1 audit)

- §4.2: re-anchored on per-day variance-reduction metric. Independent OLS sanity check (`scripts/ols_groundtruth.py`) confirmed the prior time-invariant dummy framing answered the wrong question (R² ≈ 0.0001 because chain/sector main effects average out). The new framing is identical to the group_neut production semantics and is internally consistent with §4.4.
- §4.3: fixed rolling within-group correlation bug (was demeaning within group only, producing structural -1/(k-1) negative bias). Now demeans cross-sectionally using the full universe in each window. Added a PIT-strict variant that filters by `effective_from`.
- §4.4: vectorised inner kernels (~50× speedup); scaled permutation null from 200 to 10,000 draws; replaced independent chain/sector permutation with joint `(chain, sector)` pair shuffle for two-factor schemes; added Holm-Bonferroni step-down correction over the 5 tests.
- Validated group fields under Holm-Bonferroni at α=0.05: `chain_ecosystem` (24.16% standalone reduction), `sector_code` (25.48% standalone), joint chain+sector (40.73%). `sub_sector_code` is NOT validated (14/32 active sub-sectors have n<3). `class_code` remains reference-only (4 groups, one with n=2).
