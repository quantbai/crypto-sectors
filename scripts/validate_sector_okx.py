"""validate_sector_okx.py — 10k-perm validation of the flat `sector` field on the
232-coin OKX crypto-native perp universe (v3 single-layer product).

Reuses the audited production group_neut kernel from
plans/universe_selection/build_robust_v2.py: per-day demean WITHIN FACTOR sectors,
pool RESIDUAL-labelled coins (and per-day sub-min_live groups) to OTHER then
market-neutralize. This is the conservative OTHER-collapse kernel — the honest one
(the naive within-every-label demean overstates VR; see the 2026-06 tri-lens review).

Two studies:
  (1) Per-universe variance reduction vs size-preserving permutation null
      (ALL / TOP30 / TOP50 / TOP100), nperm configurable.
  (2) Per-group cohesion: mean intra-group MARKET-RESIDUAL pairwise correlation
      vs a label-shuffle null -> FACTOR/RESIDUAL classification per the governance note.

Usage:
  python scripts/validate_sector_okx.py --n-perm 10000 --cohesion-perm 10000 \
      --outdir validation/sector_okx
"""
from __future__ import annotations
import argparse, json, time
from pathlib import Path
import numpy as np, pandas as pd

CLS = Path("classification")
RETURNS = Path("data/returns.parquet")
SEED = 42


def load():
    cls = pd.read_csv(CLS / "sector.csv")
    cls["symbol"] = cls["symbol"].str.upper()
    sec = dict(zip(cls.symbol, cls.sector))
    role = dict(zip(cls.sector, cls.role))             # label -> FACTOR/RESIDUAL (committed)
    factor = {s for s, r in role.items() if r == "FACTOR"}
    mem = json.load(open(CLS / "universe_tiers.json"))
    R = pd.read_parquet(RETURNS)
    R.columns = [c.upper() for c in R.columns]
    R = R[[c for c in R.columns if c in sec]]          # keep only labelled symbols
    return sec, role, factor, mem, R


def pooled(label_map, factor):
    return {c: (s if s in factor else "OTHER") for c, s in label_map.items()}


def production_resid(Rt, label_map, min_live=3):
    """Per-day: demean within each group with >=min_live live members; pool the
    rest (sub-min_live groups) to OTHER and demean that pool. Faithful copy of
    build_robust_v2.production_resid."""
    cols = list(Rt.columns)
    labs = np.array([label_map.get(c, "OTHER") for c in cols], dtype=object)
    rv = Rt.values
    resid = rv.copy()
    gidx = {k: np.where(labs == k)[0] for k in dict.fromkeys(labs)}
    for t in range(rv.shape[0]):
        row = rv[t]
        live = ~np.isnan(row)
        small = []
        for idx in gidx.values():
            li = idx[live[idx]]
            if len(li) == 0:
                continue
            if len(li) < min_live:
                small.extend(li.tolist())
            else:
                resid[t, li] = row[li] - row[li].mean()
        if small:
            scn = np.array(small)
            resid[t, scn] = row[scn] - row[scn].mean()
    return resid


def vr(R, sec, factor, members, min_assets, nperm, rng, tag=""):
    lbl = pooled({s: sec[s] for s in members if s in sec}, factor)
    cols = [c for c in R.columns if c in lbl]
    Rt = R[cols]
    Rt = Rt.loc[Rt.notna().sum(axis=1) >= min_assets]
    rv = Rt.values

    def pv(resid):
        with np.errstate(all="ignore"):
            tv = np.nanvar(rv, axis=1, ddof=1)
            sv = np.nanvar(resid, axis=1, ddof=1)
        n = np.sum(~np.isnan(rv), axis=1)
        ok = (n >= min_assets) & (tv > 0) & np.isfinite(tv) & np.isfinite(sv)
        return (float(np.mean(1 - sv[ok] / tv[ok])) if ok.any() else 0.0, int(ok.sum()))

    base, nd = pv(production_resid(Rt, lbl))
    syms = list(Rt.columns)
    labs = np.array([lbl[s] for s in syms], dtype=object)
    null = np.empty(nperm)
    t0 = time.time()
    for k in range(nperm):
        null[k] = pv(production_resid(Rt, dict(zip(syms, rng.permutation(labs)))))[0]
        if (k + 1) % 500 == 0:
            print(f"    [{tag}] {k+1}/{nperm} ({time.time()-t0:.0f}s)", flush=True)
    p = (np.sum(null >= base) + 1) / (nperm + 1)
    return dict(n_members=len(cols), n_days=nd, vr=base, null_mean=float(null.mean()),
                excess=base - float(null.mean()), p=p, nperm=nperm)


def cohesion(R, sec, nperm, rng):
    """Mean intra-group market-residual pairwise corr per label, vs label-shuffle null."""
    mr = R.sub(R.mean(axis=1), axis=0)              # daily cross-sectional (market) demean
    corr = mr.corr(min_periods=180)
    syms = list(corr.index)
    labs = pd.Series([sec[s] for s in syms], index=syms)

    def group_means(lab_series):
        out = {}
        for g, members in lab_series.groupby(lab_series).groups.items():
            mem = [m for m in members if m in corr.index]
            if len(mem) < 2:
                out[g] = (np.nan, len(mem)); continue
            blk = corr.loc[mem, mem].values
            iu = np.triu_indices(len(mem), k=1)
            v = blk[iu]; v = v[np.isfinite(v)]
            out[g] = (float(np.mean(v)) if len(v) else np.nan, len(mem))
        return out

    obs = group_means(labs)
    groups = list(obs.keys())
    nulls = {g: np.empty(nperm) for g in groups}
    arr = labs.values.copy()
    for k in range(nperm):
        sh = pd.Series(rng.permutation(arr), index=syms)
        gm = group_means(sh)
        for g in groups:
            nulls[g][k] = gm.get(g, (np.nan, 0))[0]
    rows = []
    for g in groups:
        o, n = obs[g]
        nl = nulls[g][np.isfinite(nulls[g])]
        p = (np.sum(nl >= o) + 1) / (len(nl) + 1) if (np.isfinite(o) and len(nl)) else np.nan
        rows.append(dict(group=g, n=n, mean_resid_corr=o,
                         null_mean=float(np.mean(nl)) if len(nl) else np.nan,
                         p=float(p) if p == p else np.nan))
    return pd.DataFrame(rows).sort_values("mean_resid_corr", ascending=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--cohesion-perm", type=int, default=5000)
    ap.add_argument("--variants", default="ALL,TOP30,TOP50,TOP100")
    ap.add_argument("--outdir", default="validation/sector_okx")
    args = ap.parse_args()
    import sys; sys.stdout.reconfigure(encoding="utf-8")
    out = Path(args.outdir); out.mkdir(parents=True, exist_ok=True)

    sec, role, factor, mem, R = load()
    print(f"[data] {R.shape[1]} symbols x {R.shape[0]} days "
          f"({str(R.index.min())[:10]} -> {str(R.index.max())[:10]})", flush=True)
    print(f"[labels] {len(set(sec[c] for c in R.columns))} sectors", flush=True)

    MA = {"ALL": 30, "TOP100": 40, "TOP50": 30, "TOP30": 20, "TOP20": 12, "TOP10": 8}
    rng = np.random.default_rng(SEED)
    res = {}
    for v in args.variants.split(","):
        members = list(R.columns) if v == "ALL" else [s.upper() for s in mem[v.lower()]]
        r = vr(R, sec, factor, members, MA[v], args.n_perm, rng, tag=v)
        res[v] = r
        print(f"[{v:6s}] n={r['n_members']:3d} VR {r['vr']*100:6.2f}%  null {r['null_mean']*100:6.2f}%"
              f"  excess {r['excess']*100:+6.2f}pp  p={r['p']:.4f}  days {r['n_days']}", flush=True)
    json.dump(res, open(out / "varred_sector.json", "w"), indent=1)

    print("\n[cohesion] per-group market-residual corr vs label-shuffle null:", flush=True)
    coh = cohesion(R, sec, args.cohesion_perm, rng)
    coh["role_json"] = coh["group"].map(role)
    coh.to_csv(out / "cohesion_sector.csv", index=False)
    for _, r in coh.iterrows():
        sig = "FACTOR" if (r.p == r.p and r.p < 0.05) else "RESIDUAL"
        print(f"  {r.group:24s} n={int(r.n):3d}  resid_corr {r.mean_resid_corr:+.3f}"
              f"  null {r.null_mean:+.3f}  p={r.p:.4f}  -> {sig}  (json:{r.role_json})", flush=True)
    print(f"\n[done] {out}", flush=True)


if __name__ == "__main__":
    main()
