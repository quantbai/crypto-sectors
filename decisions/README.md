# Classification decisions

This directory holds the audit trail for the v3 sector classification — a single
flat `sector` field over the 232-coin OKX perpetual universe.

## Structure

| File | Role |
|---|---|
| [`sector-field.md`](sector-field.md) | Master memo — methodology, sector taxonomy, and governance rules for the `sector` field |
| [`sector-field-okx-2026-06.md`](sector-field-okx-2026-06.md) | Coin-by-coin economic audit record for the 2026-06 OKX deployment (16 reassignments, adversarial verification, VR validation) |
| [`bnb.md`](bnb.md) | BNB — exchange token vs L1 rationale |
| [`pol.md`](pol.md) | POL — Network Scaling vs Smart Contract Platform |
| [`ton.md`](ton.md) | TON — sector rationale |
| [`trx.md`](trx.md) | TRX — sector rationale |
| [`wal.md`](wal.md) | WAL — sector rationale |

Per-coin files are created only for assets whose classification is non-obvious,
contested, or subject to prior discussion. Uncontested assets are covered by the
audit record alone.

## When to add a file

Add a `decisions/<asset_id>.md` for any of:

- A new asset whose sector is not obvious to a domain expert
- A reclassification of an existing asset
- Any asset that has been subject to a prior PR-level discussion

You do not need a file for assets whose classification is uncontested.

## File format

A decision document has four sections:

1. **Decision** — one-line statement of the classification chosen
2. **Context** — the asset, what it does, prior classification (if any)
3. **Considered alternatives** — what other sectors were considered, and why each was rejected
4. **Resolution rationale** — the deciding argument

Keep each section short. Reasoning before evidence.

## How to read these

Each decision is a snapshot of reasoning at the time of writing. If a decision is
later overturned, the file is **updated** (not deleted) — the old reasoning is
preserved in git history and the new reasoning is added with a date heading.

Disputes about a classification should:
1. First read the relevant `decisions/` file
2. Open an issue addressing the specific arguments there
3. PR a revised decision with new evidence

Drive-by reclassifications without engaging the existing reasoning will be closed
with a pointer to the decision file.
