# Classification decisions

This directory holds one markdown file per non-trivial classification decision. Each file is the audit trail for "why is asset X in sector Y rather than Z?"

## When to add a file here

You must add a `decisions/<asset_id>.md` for any of:

- A new asset whose sector is not obvious to a domain expert
- A reclassification of an existing asset
- Any asset that has been subject to a prior PR-level discussion

You do not need to add a file for assets whose classification is uncontested (most large-cap currencies, the major SCPs, single-product DeFi protocols).

## File format

See [CONTRIBUTING.md](../CONTRIBUTING.md#decision-document-template) for the template.

## Examples in this repository

- [`pol.md`](pol.md) — Polygon as Network Scaling vs Smart Contract Platform
- [`bnb.md`](bnb.md) — BNB as exchange token vs L1
- [`luna-symbol-history.md`](luna-symbol-history.md) — Symbol-vs-asset_id discipline across the Terra/LUNA migration

## How to read these

Each decision is a snapshot of reasoning at the time of writing. If a decision is later overturned, the file is **updated** (not deleted) — the old reasoning is preserved in git history and the new reasoning is added with a date heading.

Disputes about a classification should:
1. First read the relevant `decisions/` file
2. Open an issue addressing the specific arguments there
3. PR a revised decision with new evidence

Drive-by reclassifications without engaging the existing reasoning will be closed with a pointer to the decision file.
