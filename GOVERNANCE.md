# Governance

> Version 1.0.0-RC2 · crypto-sectors

This document defines the decision-making process for taxonomy changes, reclassifications, and dispute resolution.

---

## 1. Maintainer council

**Initial configuration (v1.0)**: sole maintainer is `@quantbai`.

Future expansion of the maintainer council requires:
- A documented nomination (GitHub Issue with `council-nomination` label)
- A minimum 14-day public comment period
- Approval by all existing council members
- Addition of the new maintainer to this file via a PR

Maintainers are responsible for: merging PRs against snapshot.csv, reviewing `decisions/` files for completeness, tagging quarterly releases, and responding to dispute issues within 14 days.

---

## 2. Quorum definition

With a sole maintainer, **quorum = 1**. This is explicit, not implicit. A single maintainer can approve and merge any PR within scope. When the council expands to N members, quorum is defined as floor(N/2) + 1 (simple majority).

---

## 3. PR merge thresholds

| Change type | Approval required |
|---|---|
| **Typo fix, whitespace, decision-doc addition** (no code change) | Maintainer alone |
| **New asset addition** (one row in snapshot.csv + decisions/ file) | Maintainer + 1 community reviewer (GitHub review approval) |
| **sub_sector_code change** (reclassification) | Maintainer + 1 community reviewer + updated decisions/ file |
| **sector_code or class_code change** | Maintainer + 2 community reviewers + updated decisions/ file + methodology.md note if policy-changing |
| **Taxonomy structural change** (new sub-sector, deprecated slot change) | Maintainer + 2 community reviewers + taxonomy.yaml version bump |
| **Governance document change** | Maintainer + 2 community reviewers + 14-day comment period |

Community reviewer: any GitHub user who has made >= 1 prior merged contribution to this repository, or who holds a verifiable affiliation with a recognized institutional research or quant organization (stated in the review comment).

**Cold-start provision (v1.0 — until council size >= 3)**: while the maintainer council has fewer than 3 active members, high-level reclassification PRs (changes to `sector_code` or `class_code`) may be merged after the maintainer posts the PR to a GitHub Issue with label `reclass-review` and at least 7 calendar days pass with no substantive objection. Objections from non-maintainers must be from contributors with a GitHub account >= 30 days old and 1+ contribution to any related open-source project. This provision lapses automatically when council reaches 3.

---

## 4. Conflict-of-interest policy

Any contributor opening a PR that touches classification of an asset in which they hold a material financial position (long or short, direct or via derivatives) **must disclose this in the PR body**. A suggested disclosure template:

> **COI Disclosure**: I hold [long/short] exposure to [SYMBOL] via [spot/perp/options/fund]. My proposed classification is [X]; I believe this is correct on the merits of the taxonomy definition, and I welcome independent review.

The maintainer must abstain from approving a PR if they personally hold the asset being reclassified. In the sole-maintainer configuration, a conflicted reclassification PR must be reviewed and approved by a community reviewer before the maintainer merges.

A maintainer who discovers an undisclosed COI after a merge may revert the PR and re-open the classification question.

---

## 5. Appeal process

An asset issuer, token holder, or external researcher who disputes a classification should:

1. Open a GitHub Issue with the `dispute` label.
2. State: (a) the asset's current classification, (b) the proposed alternative, (c) the taxonomy definition language that supports the alternative.
3. The maintainer responds within **14 calendar days** with either a rejection rationale or a request for more information.
4. If the dispute has merit, a reclassification PR is opened and follows the normal merge threshold process.
5. The final decision — whether the original classification stands or changes — is recorded in `decisions/<symbol>.md` with a reference to the issue number.

Disputes do not block the repository's operation. Disputed assets retain their current classification until a PR is merged.

---

## 6. Review frequency and release cadence

| Event | Schedule |
|---|---|
| **Quarterly snapshot tag** | Once per calendar quarter (`v2026.Q2`, `v2026.Q3`, …). Tag is created by the maintainer after CI passes and all open classification PRs from the quarter are resolved. |
| **Off-cycle emergency reclassification** | Permitted for: (a) confirmed fraud or rug-pull by a protocol, (b) stablecoin de-peg lasting > 72 hours, (c) chain migration with a new asset_id (e.g., LUNA → LUNC). Off-cycle events get a patch tag (`v2026.Q2.1`). |
| **Taxonomy version bump** | On any structural change (new sub-sector code, deprecated slot change). See `taxonomy.yaml` `version` field (SemVer). |
| **Governance review** | At each major release (v2.0+), or when council size changes. |
