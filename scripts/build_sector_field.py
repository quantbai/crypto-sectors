"""build_sector_field.py — derive the published v3 flat-`sector` artifacts from the
committed source table.

Source of truth (committed, hand-editable):
  classification/sector.csv                  symbol, sector, role, cg_id, okx_instid, audit_from, prev_label, note
  data/returns.parquet                        date x symbol log-returns (universe + PIT existence)
  validation/sector_okx/cohesion_sector.csv   per-group cohesion stats (provenance for roles.json)

Derived (regenerated, idempotent; CI asserts they stay in sync):
  classification/sector.parquet         parquet mirror of sector.csv
  classification/sector_panel.parquet   PIT (date x symbol) label matrix — the group_neut input
  classification/sector_roles.json      label -> {role, n, mean_resid_corr, cohesion_p}

PIT semantics: a coin's economic classification is time-invariant over its traded
history (label applies wherever a return exists; <NA> before listing). `audit_from`
records WHEN the label was assigned (provenance), not a regime boundary.
"""
from __future__ import annotations
import sys, json
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
CLS = Path("classification")
RETURNS = Path("data/returns.parquet")
COHESION = Path("validation/sector_okx/cohesion_sector.csv")


def main() -> int:
    static = pd.read_csv(CLS / "sector.csv")
    static["symbol"] = static["symbol"].str.upper()
    sec = dict(zip(static.symbol, static.sector))
    role = dict(zip(static.sector, static.role))            # label -> role (FACTOR/RESIDUAL)

    R = pd.read_parquet(RETURNS)
    R.columns = [c.upper() for c in R.columns]
    R = R[[c for c in R.columns if c in sec]]               # keep only labelled symbols

    # parquet mirror of the committed source
    static.to_parquet(CLS / "sector.parquet", index=False)

    # PIT panel: label where a return exists, else <NA>
    panel = pd.DataFrame(index=R.index, columns=R.columns, dtype="object")
    for c in R.columns:
        panel.loc[R[c].notna(), c] = sec[c]
    panel = panel.astype("string")
    panel.index.name = "date"
    panel.to_parquet(CLS / "sector_panel.parquet")

    # roles + cohesion provenance
    coh = pd.read_csv(COHESION).set_index("group") if COHESION.exists() else None
    roles = {}
    for lab in sorted(set(sec.values())):
        row = coh.loc[lab] if (coh is not None and lab in coh.index) else None
        roles[lab] = {
            "role": role.get(lab, "RESIDUAL"),
            "n": int((static.sector == lab).sum()),
            "mean_resid_corr": round(float(row["mean_resid_corr"]), 4) if row is not None and pd.notna(row["mean_resid_corr"]) else None,
            "cohesion_p": round(float(row["p"]), 4) if row is not None and pd.notna(row["p"]) else None,
        }
    json.dump(roles, open(CLS / "sector_roles.json", "w"), indent=1)

    nf = sum(1 for v in roles.values() if v["role"] == "FACTOR")
    print(f"[static] {len(static)} assets x {static.sector.nunique()} sectors (classification/sector.csv)")
    print(f"[panel]  {panel.shape[0]} days x {panel.shape[1]} symbols -> classification/sector_panel.parquet")
    print(f"[roles]  {nf} FACTOR / {len(roles)-nf} RESIDUAL -> classification/sector_roles.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
