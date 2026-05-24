"""
validate_schema.py
==================

Runs in CI on every PR. Asserts referential integrity between
classification/snapshot.csv and taxonomy.yaml:

  1. snapshot.csv has no duplicate asset_id
  2. snapshot.csv has no duplicate symbol
  3. Every class_code in snapshot.csv exists in taxonomy.yaml
  4. Every sector_code in snapshot.csv exists in taxonomy.yaml
  5. Every sub_sector_code in snapshot.csv exists in taxonomy.yaml
  6. Every sub_sector_code rolls up to its sector_code
  7. Every sector_code rolls up to its class_code
  8. Every chain_ecosystem value is in the tag dictionary
  9. asset_ids are lowercase, hyphen-separated
 10. symbols are uppercase

Exits 0 on success, 1 (and prints all violations) on failure.

Run locally:
    python scripts/validate_schema.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
TAXONOMY = ROOT / "taxonomy.yaml"
SNAPSHOT = ROOT / "classification" / "snapshot.csv"

ASSET_ID_RE = re.compile(r"^[a-z0-9]([a-z0-9\-]*[a-z0-9])?$")
SYMBOL_RE = re.compile(r"^[A-Z0-9]+$")


def main() -> int:
    if not TAXONOMY.exists() or not SNAPSHOT.exists():
        print("[ERROR] Missing taxonomy.yaml or classification/snapshot.csv", file=sys.stderr)
        return 1

    with TAXONOMY.open(encoding="utf-8") as f:
        tax = yaml.safe_load(f)

    classes = {c["code"] for c in tax["classes"]}
    sectors = {s["code"]: s["class_code"] for s in tax["sectors"]}
    sub_sectors = {ss["code"]: ss["sector_code"] for ss in tax["sub_sectors"]}
    chain_values = set(tax["tags"]["chain_ecosystem"]["values"].keys())

    snap = pd.read_csv(SNAPSHOT)
    errors: list[str] = []

    # 0: effective_from column — required since v1.0
    if "effective_from" not in snap.columns:
        errors.append("Missing column: effective_from (required since v1.0)")
    else:
        try:
            parsed = pd.to_datetime(snap["effective_from"])
        except Exception as exc:
            errors.append(f"effective_from not parseable as date: {exc}")
            parsed = None
        if parsed is not None and parsed.isna().any():
            null_aids = snap.loc[parsed.isna(), "asset_id"].tolist()
            errors.append(f"effective_from is null for asset_ids: {null_aids[:5]}")
        # No duplicate (asset_id, effective_from) pairs
        dup_pit = snap[snap.duplicated(["asset_id", "effective_from"], keep=False)]
        if not dup_pit.empty:
            pairs = list(zip(dup_pit["asset_id"], dup_pit["effective_from"]))
            errors.append(f"Duplicate (asset_id, effective_from) pairs: {pairs[:5]}")

    # 1: duplicate symbol (asset_id uniqueness now scoped to (asset_id, effective_from) above)
    dup_sym = snap[snap.duplicated("symbol", keep=False)]
    if not dup_sym.empty:
        errors.append(f"Duplicate symbol: {dup_sym['symbol'].tolist()}")

    # 3, 4, 5: code existence
    unknown_class = sorted(set(snap.class_code) - classes)
    if unknown_class:
        errors.append(f"Unknown class_code: {unknown_class}")
    unknown_sector = sorted(set(snap.sector_code) - set(sectors))
    if unknown_sector:
        errors.append(f"Unknown sector_code: {unknown_sector}")
    unknown_sub = sorted(set(snap.sub_sector_code) - set(sub_sectors))
    if unknown_sub:
        errors.append(f"Unknown sub_sector_code: {unknown_sub}")

    # 6: sub-sector rolls up to sector
    for _, row in snap.iterrows():
        if row.sub_sector_code in sub_sectors:
            expected = sub_sectors[row.sub_sector_code]
            if expected != row.sector_code:
                errors.append(
                    f"{row.asset_id}: sub_sector_code {row.sub_sector_code} expects "
                    f"sector_code {expected}, got {row.sector_code}"
                )

    # 7: sector rolls up to class
    for _, row in snap.iterrows():
        if row.sector_code in sectors:
            expected = sectors[row.sector_code]
            if expected != row.class_code:
                errors.append(
                    f"{row.asset_id}: sector_code {row.sector_code} expects "
                    f"class_code {expected}, got {row.class_code}"
                )

    # 8: chain values
    unknown_chain = sorted(set(snap.chain_ecosystem.dropna()) - chain_values)
    if unknown_chain:
        errors.append(f"Unknown chain_ecosystem values: {unknown_chain}")

    # 9: asset_id format
    bad_aid = [aid for aid in snap.asset_id if not ASSET_ID_RE.match(str(aid))]
    if bad_aid:
        errors.append(f"asset_id format violation (lowercase, hyphenated): {bad_aid[:5]}")

    # 10: symbol format
    bad_sym = [s for s in snap.symbol if not SYMBOL_RE.match(str(s))]
    if bad_sym:
        errors.append(f"symbol format violation (uppercase, alphanumeric): {bad_sym[:5]}")

    if errors:
        print("Schema validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"Schema validation OK — {len(snap)} assets, {len(sub_sectors)} sub-sectors, "
          f"effective_from present and valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
