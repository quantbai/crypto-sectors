"""
build_viz_data.py — compile docs/data/taxonomy.json and docs/data/validation.json
from taxonomy.yaml, classification/snapshot.csv, and validation/numbers.json.

Run: python scripts/build_viz_data.py
Idempotent: re-running produces identical sorted output.
"""

import csv
import gzip
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent
TAXONOMY_YAML = REPO / "taxonomy.yaml"
SNAPSHOT_CSV = REPO / "classification" / "snapshot.csv"
NUMBERS_JSON = REPO / "validation" / "numbers.json"
DECISIONS_DIR = REPO / "decisions"
OUT_DIR = REPO / "docs" / "data"
OUT_TAXONOMY = OUT_DIR / "taxonomy.json"
OUT_VALIDATION = OUT_DIR / "validation.json"
REPO_URL = "https://github.com/quantbai/crypto-sectors"

# Column order for chain_sector_matrix — hard-coded per DESIGN-AMENDMENTS §3.2
CHAIN_ORDER = ["BTC", "ETH", "SOL", "BNB", "AVAX", "TRX", "COSMOS", "NEAR", "MOVE", "OTHER"]


def load_yaml():
    with open(TAXONOMY_YAML, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_snapshot():
    rows = []
    with open(SNAPSHOT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "asset_id": row["asset_id"],
                "symbol": row["symbol"],
                "name": row["name"],
                "class_code": int(row["class_code"]),
                "sector_code": int(row["sector_code"]),
                "sub_sector_code": int(row["sub_sector_code"]),
                "chain_ecosystem": row["chain_ecosystem"],
                "effective_from": row["effective_from"],
            })
    return rows


def load_numbers():
    with open(NUMBERS_JSON, encoding="utf-8") as f:
        raw = f.read()
    # Replace NaN (invalid JSON) with null
    raw = raw.replace(": NaN", ": null").replace(":NaN", ":null")
    return json.loads(raw)


def decision_url(asset_id: str) -> str | None:
    md = DECISIONS_DIR / f"{asset_id}.md"
    if md.exists():
        return f"{REPO_URL}/blob/main/decisions/{asset_id}.md"
    return None


def build_taxonomy(tax: dict, assets: list) -> dict:
    # Index structures
    classes = {c["code"]: c for c in tax["classes"]}
    sectors = {s["code"]: s for s in tax["sectors"]}
    sub_sectors = {ss["code"]: ss for ss in tax["sub_sectors"]}

    # Build asset lookup by sub_sector_code
    assets_by_sub = defaultdict(list)
    for a in assets:
        assets_by_sub[a["sub_sector_code"]].append(a)

    # Sort assets within each sub-sector by symbol for determinism
    for code in assets_by_sub:
        assets_by_sub[code].sort(key=lambda x: x["symbol"])

    # Hierarchy: class -> sector -> sub_sector -> assets
    # Group sectors by class, sub_sectors by sector
    sectors_by_class = defaultdict(list)
    for s in tax["sectors"]:
        sectors_by_class[s["class_code"]].append(s)

    sub_sectors_by_sector = defaultdict(list)
    for ss in tax["sub_sectors"]:
        sub_sectors_by_sector[ss["sector_code"]].append(ss)

    # Build nested hierarchy for D3
    def make_asset_node(a):
        return {
            "asset_id": a["asset_id"],
            "symbol": a["symbol"],
            "name": a["name"],
            "chain_ecosystem": a["chain_ecosystem"],
            "effective_from": a["effective_from"],
            "decision_doc": decision_url(a["asset_id"]),
        }

    def make_sub_sector_node(ss, ss_assets):
        # Sort siblings by asset count desc, code asc (DESIGN-AMENDMENTS §1.2)
        # Siblings are all sub-sectors under same parent; sorted at build time
        node = {
            "code": ss["code"],
            "name": ss["name"],
            "is_extension": ss.get("is_extension", False),
            "assets": [make_asset_node(a) for a in ss_assets],
        }
        return node

    def make_sector_node(s):
        # Get sub-sectors, sort by asset count desc, then code asc
        subs = sub_sectors_by_sector.get(s["code"], [])
        subs_with_count = []
        for ss in subs:
            count = len(assets_by_sub.get(ss["code"], []))
            subs_with_count.append((count, ss["code"], ss))
        subs_with_count.sort(key=lambda x: (-x[0], x[1]))

        sub_nodes = []
        for _, _, ss in subs_with_count:
            ss_assets = assets_by_sub.get(ss["code"], [])
            sub_nodes.append(make_sub_sector_node(ss, ss_assets))

        node = {
            "code": s["code"],
            "name": s["name"],
            "children": sub_nodes,
        }
        return node

    def make_class_node(c):
        # Sectors sorted by total asset count desc, then code asc
        sectors_in_class = sectors_by_class.get(c["code"], [])
        sectors_with_count = []
        for s in sectors_in_class:
            count = sum(
                len(assets_by_sub.get(ss["code"], []))
                for ss in sub_sectors_by_sector.get(s["code"], [])
            )
            sectors_with_count.append((count, s["code"], s))
        sectors_with_count.sort(key=lambda x: (-x[0], x[1]))

        sector_nodes = [make_sector_node(s) for _, _, s in sectors_with_count]
        node = {
            "code": c["code"],
            "name": c["name"],
            "children": sector_nodes,
        }
        return node

    # Sort classes by total asset count desc, code asc
    classes_with_count = []
    for c in tax["classes"]:
        count = sum(
            len(assets_by_sub.get(ss["code"], []))
            for s in sectors_by_class.get(c["code"], [])
            for ss in sub_sectors_by_sector.get(s["code"], [])
        )
        classes_with_count.append((count, c["code"], c))
    classes_with_count.sort(key=lambda x: (-x[0], x[1]))

    class_nodes = [make_class_node(c) for _, _, c in classes_with_count]

    hierarchy = {
        "name": "crypto-sectors",
        "children": class_nodes,
    }

    # assets_flat for search index — codes only, names referenced from hierarchy at render
    assets_flat = []
    for a in sorted(assets, key=lambda x: x["symbol"]):
        # Look up names
        cls = classes[a["class_code"]]
        sec = sectors[a["sector_code"]]
        ss = sub_sectors[a["sub_sector_code"]]
        assets_flat.append({
            "asset_id": a["asset_id"],
            "symbol": a["symbol"],
            "name": a["name"],
            "class_code": a["class_code"],
            "class_name": cls["name"],
            "sector_code": a["sector_code"],
            "sector_name": sec["name"],
            "sub_sector_code": a["sub_sector_code"],
            "sub_sector_name": ss["name"],
            "chain_ecosystem": a["chain_ecosystem"],
            "effective_from": a["effective_from"],
            "decision_doc": decision_url(a["asset_id"]),
        })

    # chain_sector_matrix
    # Rows = sectors (sorted by total asset count desc, code asc)
    sector_total = defaultdict(int)
    cell_map = defaultdict(list)  # (sector_code, chain) -> [asset_id, ...]

    for a in assets:
        key = (a["sector_code"], a["chain_ecosystem"])
        chain = a["chain_ecosystem"] if a["chain_ecosystem"] in CHAIN_ORDER else "OTHER"
        key_norm = (a["sector_code"], chain)
        cell_map[key_norm].append(a["asset_id"])
        sector_total[a["sector_code"]] += 1

    # Sectors sorted by total desc, code asc
    all_sector_codes = sorted(sector_total.keys(), key=lambda c: (-sector_total[c], c))
    sector_rows = [{"code": c, "name": sectors[c]["name"]} for c in all_sector_codes]

    cells = []
    for sc in all_sector_codes:
        for chain in CHAIN_ORDER:
            ids = sorted(cell_map.get((sc, chain), []))
            if ids:
                cells.append({
                    "chain": chain,
                    "sector_code": sc,
                    "asset_ids": ids,
                    "count": len(ids),
                })

    chain_sector_matrix = {
        "chains": CHAIN_ORDER,
        "sectors": sector_rows,
        "cells": cells,
    }

    # Count active sub-sectors (with at least 1 asset)
    n_active_sub_sectors = sum(
        1 for code in sub_sectors if len(assets_by_sub.get(code, [])) > 0
    )
    n_sub_sectors_total = len(sub_sectors)

    # Metadata
    n_assets = len(assets)
    n_classes = len(classes)
    n_sectors = len(sectors)

    snapshot_date = sorted(assets, key=lambda a: a["effective_from"])[0]["effective_from"]

    metadata = {
        "version": tax.get("version", "1.0.0"),
        "n_assets": n_assets,
        "n_classes": n_classes,
        "n_sectors": n_sectors,
        "n_sub_sectors": n_sub_sectors_total,
        "n_active_sub_sectors": n_active_sub_sectors,
        "snapshot_date": snapshot_date,
        "repo_url": REPO_URL,
    }

    return {
        "metadata": metadata,
        "hierarchy": hierarchy,
        "assets_flat": assets_flat,
        "chain_sector_matrix": chain_sector_matrix,
    }


def build_validation(numbers: dict) -> dict:
    """Flatten validation/numbers.json into the headline shape the UI needs."""

    def safe(v):
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return None
        return v

    headline = {
        # E1 sector spread
        "sector_spread": safe(numbers.get("e1_sector_spread")),
        "sector_spread_ci_lo": safe(numbers.get("e1_sector_ci_lo")),
        "sector_spread_ci_hi": safe(numbers.get("e1_sector_ci_hi")),
        # E4 rolling windows
        "rolling_n_positive": safe(numbers.get("e4_n_windows_spread_positive")),
        "rolling_n_total": safe(numbers.get("e4_n_windows")),
        # E5 chain vs sector comparison (DESIGN-AMENDMENTS §5.1)
        "spread_ours": safe(numbers.get("e5_spread_ours")),
        "spread_chain": safe(numbers.get("e5_spread_chain")),
        # E6 variance decomposition
        "group_neut_variance_pct": safe(numbers.get("e6_alpha_variance_between_sector_pct")),
        "ic_sharpe_raw": safe(numbers.get("e6_ic_sharpe_raw")),
        "ic_sharpe_sector_demeaned": safe(numbers.get("e6_ic_sharpe_sector_demeaned")),
        # Sub-sector Holm survivors
        "n_sub_sectors_survive_holm": safe(numbers.get("e2_n_survive_holm_05")),
        "n_sub_sectors_tested": safe(numbers.get("e2_n_tested")),
    }

    per_sub_sector = []
    for entry in numbers.get("e2_sub_sectors", []):
        per_sub_sector.append({
            "code": entry["code"],
            "name": entry["name"],
            "n_members": entry.get("n"),
            "rho_within": safe(entry.get("rho_within")),
            "z_score": safe(entry.get("z")),
            "verdict": entry.get("verdict", "underpowered"),
        })

    # Sort by code for determinism
    per_sub_sector.sort(key=lambda x: x["code"])

    return {
        "headline": headline,
        "per_sub_sector": per_sub_sector,
    }


def json_dumps_sorted(obj) -> str:
    """Serialize with sorted keys for determinism."""
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)


def main():
    print("[viz] Loading source files...")
    tax = load_yaml()
    assets = load_snapshot()
    numbers = load_numbers()

    print(f"[viz] Loaded {len(assets)} assets from snapshot.csv")

    taxonomy_out = build_taxonomy(tax, assets)
    validation_out = build_validation(numbers)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Write taxonomy.json
    tax_str = json_dumps_sorted(taxonomy_out)
    OUT_TAXONOMY.write_text(tax_str, encoding="utf-8")

    # Measure gzipped size
    gz_bytes = gzip.compress(tax_str.encode("utf-8"), compresslevel=9)
    gz_kb = len(gz_bytes) / 1024

    # Write validation.json
    val_str = json_dumps_sorted(validation_out)
    OUT_VALIDATION.write_text(val_str, encoding="utf-8")

    meta = taxonomy_out["metadata"]
    print(
        f"[viz] Built {OUT_TAXONOMY.relative_to(REPO)}: "
        f"{meta['n_classes']} classes / {meta['n_sectors']} sectors / "
        f"{meta['n_sub_sectors']} sub-sectors ({meta['n_active_sub_sectors']} active) / "
        f"{meta['n_assets']} assets | gzipped: {gz_kb:.1f} KB"
    )
    print(f"[viz] Built {OUT_VALIDATION.relative_to(REPO)}")

    if gz_kb > 30:
        print(f"[viz] WARNING: taxonomy.json gzipped is {gz_kb:.1f} KB — exceeds 30 KB target")
        sys.exit(1)

    print("[viz] Done.")


if __name__ == "__main__":
    main()
