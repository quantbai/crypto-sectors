# Changelog

All notable changes to crypto-sectors are documented here.

Format: `[vX.Y.Z] YYYY-MM-DD — N assets — Summary`.

---

## [v1.0.0] — Pending (target: 2026-Q2)

**158 assets · 4 classes · 14 sectors · ~35 sub-sectors**

Changes from v1.0-RC2:

- Version string bumped from `1.0.0-RC2` to `1.0.0` in `methodology.md` and `taxonomy.yaml`
- Final CI green on all checks required before tag is pushed
- No content changes from RC2

---

## [v1.0.0-RC2] — 2026-05-24

**158 assets · 4 classes · 14 sectors · ~35 sub-sectors**

Changes from v1.0-RC1 (this batch, QD-A scope):

- **Schema: `effective_from` column added to `classification/snapshot.csv`** (all 158 rows = `2024-05-23`, the min date in `data/daily_returns.parquet`). Establishes SCD-lite PIT semantics: reclassifications from v1.1 onward will add new rows with later `effective_from` dates rather than overwriting existing rows.
- **PRIME reclassification**: sub_sector_code `301092` (RWA Issuer — Governance, sector 3010 DeFi) → `305020` (Gaming, sector 3050 Metaverse). Echelon Prime is a gaming-economy protocol for AAA studios, not an RWA issuer. See `decisions/prime.md`.
- **Datonomy affiliation language corrected**: removed unsubstantiated "round-trip compatibility" claim from `methodology.md §3.2`, `§7`, and `taxonomy.yaml` header. Replaced with factual disclaimer per D2 in the upgrade plan.
- **New documents added**: `SCHEMA.md`, `UNIVERSE.md`, `GOVERNANCE.md`, `CHANGELOG.md`.
- **`decisions/luna-symbol-history.md` corrected**: `terra-luna-original` → `terra-luna-classic` to match snapshot asset_id.
- **`methodology.md §4.2`**: added PIT immutability contract and git-tag warning.
- **`methodology.md §5`**: "Universe filters" reworded to "investable filters" to clarify coverage vs tradability distinction.
- **`methodology.md` version**: `1.0.0` → `1.0.0-RC2`.

---

## [v1.0.0-RC1] — 2026-05-23

**158 assets · 4 classes · 14 sectors · ~35 sub-sectors**

Initial public release candidate. Built from scratch over one development sprint.

Key decisions baked in at RC1:

- Three-level hierarchy (class → sector → sub-sector) sized for a universe of ~150–300 assets, matching precedent from institutional equity classification systems adjusted for digital-asset universe size.
- `chain_ecosystem` as an orthogonal tag rather than a hierarchy level; chain effects in crypto can rival sector effects and forcing them into the hierarchy distorts both axes.
- Sub-sector codes ending `90`–`99` reserved as community extensions (e.g., 301090 Liquid Staking, 301091 Liquid Restaking).
- 6-digit `CCSSXX` positional code format chosen to make potential future crosswalks to institutional classification systems tractable.
- `asset_id` (stable, lowercase, hyphenated) as canonical key; `symbol` in a lookup table. Handles LUNA/LUNC collision and MATIC/POL rename correctly.
- Empirical validation via within-vs-between correlation bootstrap (results in `validation.md`).
- CI: referential integrity check (`validate_schema.py`) + CSV content equality.

Pre-RC1 development history (not tagged):

- **v0.2** (internal): Merged `304091` (DePIN Compute), `304092` (DePIN AI), `304093` (AI Agents) into `304020` (Compute & Private Storage) after intra-group correlations were negative on split. Deprecated slots documented in `taxonomy.yaml`. Added `202090` (Restaking Infrastructure) deprecated slot after EIGEN moved to 301091.
- **v0.1** (internal): Initial 4-class skeleton. DEX / Lending / L1 / L2 as the primary sectors. DePIN split into three sub-sectors (later merged in v0.2). No empirical validation yet.

---

## Known open issues — v1.0.1 candidates

- **PENGU classification**: currently `102010` (Meme Coins). Under review for possible reclassification to `305030` (NFT Ecosystems) given Pudgy Penguins' NFT collection origin. Needs correlation evidence. Track in GitHub Issues.

---

## v1.1 Forward contract — `reclassifications.csv`

Starting in v1.1, all reclassification events will be recorded in a dedicated audit file `classification/reclassifications.csv`. This is a commitment, not a v1.0 deliverable.

**Planned schema (5 columns)**:

| Column | dtype | Description |
|---|---|---|
| `asset_id` | string | Stable asset identifier (join key) |
| `field` | string | Which field changed: `class_code`, `sector_code`, `sub_sector_code`, or `chain_ecosystem` |
| `old_value` | string | Value before the reclassification (stored as string to handle mixed types) |
| `new_value` | string | Value after the reclassification |
| `effective_from` | date | Date from which the new value applies; matches the new row in `snapshot.csv` |

Each row in `reclassifications.csv` corresponds to one new row added to `snapshot.csv` with a later `effective_from`. The old row in `snapshot.csv` is never deleted — it remains as historical record.
