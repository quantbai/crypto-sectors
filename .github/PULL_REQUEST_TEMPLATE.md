## What this PR changes

<!-- One-line summary: "Add SYMBOL to sector X" / "Reclassify SYMBOL from X to Y" / "Add sub-sector NNNNNN" -->

## Type

- [ ] New asset
- [ ] Reclassification of existing asset
- [ ] New sub-sector proposal (requires prior issue discussion)
- [ ] Taxonomy structural change
- [ ] Methodology / documentation update
- [ ] Script / CI fix

## Rationale

<!-- For new assets and reclassifications: what does this asset do economically?
     Where does value accrue? What were the alternative candidates?
     For sub-sector proposals: paste the issue discussion summary. -->

## Decision document

<!-- For new assets with non-obvious classification, or for any reclassification:
     confirm a `decisions/<asset_id>.md` is included in this PR. -->

- [ ] `decisions/<asset_id>.md` added or updated
- [ ] Not applicable (classification is uncontested)

## Checklist

- [ ] `python scripts/validate_schema.py` passes locally
- [ ] `python scripts/build_matrices.py` regenerated matrices committed
- [ ] No more than 5 assets touched in this PR (otherwise open an issue first)
