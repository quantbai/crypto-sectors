# CVX — Convex Finance

**asset_id**: `cvx`
**Current classification**: sector_code=`3010` (Decentralized Finance), sub_sector=`301060` (Asset Management), chain_ecosystem=`ETH`
**Current sector cohesion**: +0.009, LOW (sector-level)

## What it is

Convex is a meta-protocol on top of Curve (and Frax) that aggregates veCRV voting power. Users deposit CRV → receive cvxCRV (liquid wrapper) or LP tokens → Convex deposits to Curve gauges, votes with accumulated veCRV, and boosts LP yield. CVX is the governance/value-accrual token of this aggregation layer.

## Value accrual mechanism

CVX stakers (vlCVX = vote-locked CVX) direct Convex's massive veCRV voting power, earn bribes via Votium/Hidden Hand for that vote-direction, and capture a cut of CRV emissions plus performance fees on cvxCRV. Convex's economic profile is therefore derivative of Curve's gauge economics — CVX is essentially leveraged exposure to veCRV politics and bribe markets.

## Economic siblings

CRV (direct dependency). PENDLE (other yield-extraction protocol but mechanistically different). Less direct: AURA (Balancer wrapper, similar pattern, not in our universe).

## Classification verdict

- **Keep current**: `301060 Asset Management`
- Rationale: Yield-aggregator / boost-wrapper rather than a DEX or lender. Distinct economic engine from spot DEX (depends on Curve emissions and bribe markets). Should be grouped with PENDLE under a "Yield aggregation / yield derivatives" sub-cohort.
