## What this PR changes

<!-- One-line summary: "Add SYMBOL to sector X" / "Reclassify SYMBOL from X to Y" / "Taxonomy/doc update" -->

## Type

- [ ] New asset (add to `classification/sector.csv`)
- [ ] Reclassification of existing asset
- [ ] Taxonomy / label definition change (`taxonomy.yaml`)
- [ ] Methodology / documentation update
- [ ] Script / CI fix

## Economic rationale

<!-- For new assets and reclassifications:
     - What does this asset do economically?
     - Where does value accrue, and to whom?
     - Which sector boundary rule in taxonomy.yaml applies?
     - What were the alternative sector candidates, and why rejected?
     Omit for doc/script-only PRs. -->

## Decision document

- [ ] `decisions/<cg_id>.md` added or updated (required for non-obvious classifications and reclassifications)
- [ ] Not applicable (doc/script/CI change only)

## Checklist

- [ ] `python scripts/validate_schema.py` passes locally (exit 0)
- [ ] `python scripts/build_sector_field.py` re-run; derived artifacts committed (`sector.parquet`, `sector_panel.parquet`, `sector_roles.json`)
- [ ] No reference to 4-tier hierarchy (class_code, sector_code, sub_sector_code, chain_ecosystem) introduced
- [ ] No more than 5 assets reclassified in a single PR (larger batches require a prior issue)
