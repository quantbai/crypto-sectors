# scripts/

Reproducible pipeline for crypto-sectors v3.

## Pipeline order

```
classification/sector.csv  (committed source of truth — edit this)
  -> validate_schema.py          CI gate: referential integrity
  -> build_sector_field.py       Derive classification/sector.parquet,
                                   classification/sector_panel.parquet,
                                   classification/sector_roles.json
  -> validate_sector_okx.py      10k-perm variance-reduction + cohesion validation
```

Returns data:

```
data/returns.parquet   (232-symbol daily log-returns — provided artifact, built offline from OKX data)
```

`data/returns.parquet` is not regenerated in-repo. It is a provided artifact sourced from OKX USDT-margined perpetual OHLCV data, built offline. The in-repo pipeline only reads it.

## Scripts

| Script | Purpose |
|---|---|
| `validate_schema.py` | Asserts referential integrity: every `sector` label in `classification/sector.csv` exists in `taxonomy.yaml`; `cg_id` and `okx_instid` are non-null and unique; `role` is one of `FACTOR`/`RESIDUAL`/`OTHER`. Exit 0 = green CI gate. |
| `build_sector_field.py` | Reads `classification/sector.csv` and derives three artifacts: `classification/sector.parquet` (flat mirror), `classification/sector_panel.parquet` (date × symbol PIT label matrix, `<NA>` before listing date), and `classification/sector_roles.json` (label → `{role, n, mean_resid_corr, cohesion_p}`). Must be re-run and artifacts committed after any edit to `sector.csv`. |
| `validate_sector_okx.py` | 10,000-permutation (size-preserving label-shuffle) variance-reduction and intra-group cohesion test against the production OTHER-collapse kernel. Writes `validation/sector_okx/varred_sector.json`, `cohesion_sector.csv`, `run_10k.log`, `REPORT.md`. Full run ~1.5 h; use `--n-perm 200` for smoke. |

## Quick start

```bash
# 1. Verify integrity after editing sector.csv
python scripts/validate_schema.py

# 2. Rebuild derived artifacts
python scripts/build_sector_field.py

# 3. Full validation (10k perms, ~1.5 h)
python scripts/validate_sector_okx.py --n-perm 10000

# 4. Smoke validation (fast)
python scripts/validate_sector_okx.py --n-perm 200
```
