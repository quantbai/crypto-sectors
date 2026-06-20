"""
validate_schema.py
==================

Validates referential integrity of the v3 flat-sector product. Run in CI on
every PR; run locally before any commit that touches classification/ or
taxonomy.yaml.

Checks
------
1. classification/sector.csv has exactly the 8 expected columns, 232 rows,
   and no missing symbol / sector / role values.
2. Every sector label in sector.csv is defined in taxonomy.yaml's flat label
   set (sector_field.labels + sector_field.okx_universe_amendments[*].label);
   every taxonomy-defined label that appears in sector.csv exists in the file
   (inactive labels such as tron_ecosystem / onchain_derivatives may be absent
   without error).
3. Every role value in sector.csv is exactly FACTOR or RESIDUAL.
4. Every symbol in classification/universe_tiers.json (all tiers) exists in
   sector.csv.
5. data/returns.parquet covers every symbol in sector.csv (i.e., each symbol
   has a returns column; extra columns in the parquet are allowed).
6. classification/sector_roles.json label set == sector.csv unique label set
   (exact match in both directions).

Exits 0 and prints an OK summary on success.
Exits 1 and prints all specific failure messages on any check failure.

Run locally:
    python scripts/validate_schema.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent

SECTOR_CSV     = ROOT / "classification" / "sector.csv"
TAXONOMY       = ROOT / "taxonomy.yaml"
UNIVERSE_TIERS = ROOT / "classification" / "universe_tiers.json"
SECTOR_ROLES   = ROOT / "classification" / "sector_roles.json"
RETURNS        = ROOT / "data" / "returns.parquet"

EXPECTED_COLUMNS = ["symbol", "sector", "role", "cg_id", "okx_instid",
                    "audit_from", "prev_label", "note"]
EXPECTED_ROWS    = 232
VALID_ROLES      = {"FACTOR", "RESIDUAL"}


def load_taxonomy_labels(tax: dict) -> set[str]:
    """Return all flat sector label names defined in taxonomy.yaml.

    v3 taxonomy is a single flat layer: all 15 labels (including the
    non-directional residual pool ``OTHER``) live under the top-level
    ``labels`` list, each as ``{name, role, cohesion_mean_resid_corr, ...}``.
    """
    return {lbl["name"] for lbl in tax["labels"]}


def load_taxonomy_roles(tax: dict) -> dict[str, str]:
    """label -> role (FACTOR/RESIDUAL) as declared in taxonomy.yaml."""
    return {lbl["name"]: lbl.get("role") for lbl in tax["labels"]}


def main() -> int:
    errors: list[str] = []

    # ------------------------------------------------------------------
    # Pre-flight: required files
    # ------------------------------------------------------------------
    missing_files = [
        p for p in (SECTOR_CSV, TAXONOMY, UNIVERSE_TIERS, SECTOR_ROLES, RETURNS)
        if not p.exists()
    ]
    if missing_files:
        for p in missing_files:
            print(f"[ERROR] Missing required file: {p.relative_to(ROOT)}", file=sys.stderr)
        return 1

    # ------------------------------------------------------------------
    # Load inputs
    # ------------------------------------------------------------------
    sec = pd.read_csv(SECTOR_CSV, dtype=str, keep_default_na=False)

    with TAXONOMY.open(encoding="utf-8") as f:
        tax = yaml.safe_load(f)

    with UNIVERSE_TIERS.open(encoding="utf-8") as f:
        tiers: dict[str, list[str]] = json.load(f)

    with SECTOR_ROLES.open(encoding="utf-8") as f:
        roles_json: dict = json.load(f)

    # ------------------------------------------------------------------
    # CHECK 1: columns, row count, non-null required fields
    # ------------------------------------------------------------------
    actual_cols = list(sec.columns)
    if actual_cols != EXPECTED_COLUMNS:
        errors.append(
            f"CHECK 1 FAIL — column mismatch.\n"
            f"  expected : {EXPECTED_COLUMNS}\n"
            f"  got      : {actual_cols}"
        )

    if len(sec) != EXPECTED_ROWS:
        errors.append(
            f"CHECK 1 FAIL — row count: expected {EXPECTED_ROWS}, got {len(sec)}"
        )

    for col in ("symbol", "sector", "role"):
        if col in sec.columns:
            blank = sec[sec[col].str.strip() == ""]
            if not blank.empty:
                errors.append(
                    f"CHECK 1 FAIL — missing/blank '{col}' for symbols: "
                    f"{blank['symbol'].tolist()[:10]}"
                )

    # ------------------------------------------------------------------
    # CHECK 2: sector labels in sector.csv are all defined in taxonomy.yaml
    # ------------------------------------------------------------------
    taxonomy_labels = load_taxonomy_labels(tax)
    csv_labels      = set(sec["sector"].unique())

    unknown_in_csv = csv_labels - taxonomy_labels
    if unknown_in_csv:
        errors.append(
            f"CHECK 2 FAIL — sector labels in sector.csv not defined in taxonomy.yaml: "
            f"{sorted(unknown_in_csv)}"
        )

    # (Reverse: taxonomy labels absent from sector.csv are inactive, not an error.)

    # ------------------------------------------------------------------
    # CHECK 3: every role is FACTOR or RESIDUAL
    # ------------------------------------------------------------------
    if "role" in sec.columns:
        bad_roles = set(sec["role"].unique()) - VALID_ROLES
        if bad_roles:
            errors.append(
                f"CHECK 3 FAIL — invalid role values (must be FACTOR or RESIDUAL): "
                f"{sorted(bad_roles)}"
            )

    # ------------------------------------------------------------------
    # CHECK 4: every symbol in universe_tiers.json exists in sector.csv
    # ------------------------------------------------------------------
    sector_symbols = set(sec["symbol"])
    all_tier_symbols: set[str] = set()
    for symbols in tiers.values():
        all_tier_symbols |= set(symbols)

    missing_from_sec = all_tier_symbols - sector_symbols
    if missing_from_sec:
        errors.append(
            f"CHECK 4 FAIL — universe_tiers.json symbols not in sector.csv: "
            f"{sorted(missing_from_sec)}"
        )

    # ------------------------------------------------------------------
    # CHECK 5: returns.parquet covers every sector.csv symbol
    # ------------------------------------------------------------------
    try:
        ret_cols = set(pd.read_parquet(RETURNS).columns)
    except Exception as exc:
        errors.append(f"CHECK 5 FAIL — cannot read data/returns.parquet: {exc}")
        ret_cols = set()

    if ret_cols:
        missing_in_ret = sector_symbols - ret_cols
        if missing_in_ret:
            errors.append(
                f"CHECK 5 FAIL — sector.csv symbols absent from data/returns.parquet: "
                f"{sorted(missing_in_ret)}"
            )

    # ------------------------------------------------------------------
    # CHECK 6: sector_roles.json label set == sector.csv label set
    # ------------------------------------------------------------------
    roles_json_labels = set(roles_json.keys())

    in_roles_not_csv = roles_json_labels - csv_labels
    in_csv_not_roles = csv_labels - roles_json_labels

    if in_roles_not_csv:
        errors.append(
            f"CHECK 6 FAIL — labels in sector_roles.json but not in sector.csv: "
            f"{sorted(in_roles_not_csv)}"
        )
    if in_csv_not_roles:
        errors.append(
            f"CHECK 6 FAIL — labels in sector.csv but not in sector_roles.json: "
            f"{sorted(in_csv_not_roles)}"
        )

    # ------------------------------------------------------------------
    # CHECK 7: taxonomy.yaml role declaration matches sector.csv role per label
    # ------------------------------------------------------------------
    tax_roles = load_taxonomy_roles(tax)
    csv_roles = dict(zip(sec["sector"], sec["role"]))
    role_mismatch = {
        lab: {"sector.csv": csv_roles[lab], "taxonomy.yaml": tax_roles.get(lab)}
        for lab in csv_labels
        if lab in tax_roles and tax_roles[lab] != csv_roles[lab]
    }
    if role_mismatch:
        errors.append(
            f"CHECK 7 FAIL — role disagreement between sector.csv and taxonomy.yaml: "
            f"{role_mismatch}"
        )

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    if errors:
        print("Schema validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    n_sectors   = len(csv_labels)
    n_tiers     = len(tiers)
    tier_counts = {k: len(v) for k, v in tiers.items()}
    print(
        f"Schema validation OK — "
        f"{len(sec)} rows, {n_sectors} sector labels, "
        f"{n_tiers} tiers ({tier_counts}), "
        f"all {len(sector_symbols)} symbols covered in returns.parquet."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
