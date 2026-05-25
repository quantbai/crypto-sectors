"""
fetch_descriptions.py — Pull asset descriptions from CoinGecko API v3.

Rationale:
    Human-readable descriptions enrich every per-asset deep page. CoinGecko
    provides free, CC-BY-licensed descriptions covering most assets in our
    universe. We cache the result in data/descriptions.json so CI never depends
    on network availability.

Inputs:
    classification/snapshot.csv — 158 active asset rows (asset_id, symbol, name, ...)

Outputs:
    data/descriptions.json — per-asset descriptions (committed, not regenerated in CI)
    data/descriptions.MISSING.txt — assets that could not be fetched (informational)

Failure modes:
    - CoinGecko down: writes MISSING.txt, exits 0 (existing descriptions.json untouched)
    - Asset not on CoinGecko: sets ok=false, short_desc=null
    - Rate-limit hit: exponential backoff up to 60s; after 3 retries per asset, marks missing
    - Network error on any asset: logged, asset marked missing, script continues

Idempotency:
    The script overwrites data/descriptions.json deterministically given the same
    CoinGecko responses. The 'fetched_at' fields use date-only strings (no wall-clock
    time), so the file is stable across reruns on the same day.

Usage:
    python scripts/fetch_descriptions.py [--dry-run]
    --dry-run: print CoinGecko ids that would be fetched, do not make HTTP calls
"""

import csv
import html
import json
import os
import re
import sys
import time
import argparse
from pathlib import Path
from urllib import request, error

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_CSV = REPO_ROOT / "classification" / "snapshot.csv"
DATA_DIR = REPO_ROOT / "data"
OUT_JSON = DATA_DIR / "descriptions.json"
MISSING_TXT = DATA_DIR / "descriptions.MISSING.txt"

SCHEMA_VERSION = "1.0"
SOURCE = "CoinGecko API v3"
ATTRIBUTION_URL = "https://www.coingecko.com"
CG_BASE = "https://api.coingecko.com/api/v3"
SLEEP_BETWEEN = 4.0   # seconds; free tier ~15 req/min with margin
MAX_RETRIES = 3
BACKOFF_BASE = 6.0    # exponential backoff base seconds

# ---------------------------------------------------------------------------
# Manual CoinGecko id overrides.
#
# When asset_id does not match CoinGecko's slug, provide the correct slug here.
# Rationale for each entry documented inline.
# Discovery method: CoinGecko /search endpoint + manual verification.
# ---------------------------------------------------------------------------
CG_ID_OVERRIDES = {
    # asset_id            CoinGecko slug
    "btc":               "bitcoin",          # added 2026-05-25 after retry
    "eth":               "ethereum",         # added 2026-05-25 after retry
    "sol":               "solana",           # added 2026-05-25 after retry
    "bnb":               "binancecoin",
    "xrp":               "ripple",
    "trx":               "tron",
    "doge":              "dogecoin",
    "hype":              "hyperliquid",
    "zec":               "zcash",
    "ada":               "cardano",
    "bch":               "bitcoin-cash",
    "xmr":               "monero",
    "link":              "chainlink",
    "cc":                "canton-network",   # Canton Network
    "ton":               "toncoin",
    "xlm":               "stellar",
    "sui":               "sui",
    "ltc":               "litecoin",
    "avax":              "avalanche-2",
    "hbar":              "hedera-hashgraph",
    "shib":              "shiba-inu",
    "cro":               "crypto-com-chain",
    "near":              "near",
    "xaut":              "tether-gold",
    "tao":               "bittensor",
    "uni":               "uniswap",
    "dot":               "polkadot",
    "mnt":               "mantle",
    "paxg":              "pax-gold",
    "wlfi":              "world-liberty-financial",
    "ondo":              "ondo-finance",
    "aster":             "astar",            # Astar Network
    "okb":               "okb",
    "sky":               "sky",
    "pi":                "pi-network",
    "pepe":              "pepe",
    "icp":               "internet-computer",
    "etc":               "ethereum-classic",
    "aave":              "aave",
    "morpho":            "morpho",
    "qnt":               "quant-network",
    "atom":              "cosmos",
    "algo":              "algorand",
    "render":            "render-token",
    "pol":               "matic-network",    # POL is Polygon's new token, same CG entry
    "wld":               "worldcoin-wld",
    "kas":               "kaspa",
    "ena":               "ethena",
    "nexo":              "nexo",
    "vvv":               "venice-token",
    "jst":               "just",
    "apt":               "aptos",
    "fil":               "filecoin",
    "flr":               "flare-networks",
    "arb":               "arbitrum",
    "jup":               "jupiter-exchange-solana",  # corrected 2026-05-25 (was jupiter-ag, 404)
    "xdc":               "xdce-crowd-sale",
    "pump":              "pump-fun",
    "pengu":             "pudgy-penguins",
    "vet":               "vechain",
    "dash":              "dash",
    "inj":               "injective-protocol",
    "night":             "midnight-2",       # Midnight (IOG)
    "bonk":              "bonk",
    "virtual":           "virtual-protocol",
    "trump":             "official-trump",
    "cake":              "pancakeswap-token",
    "fet":               "fetch-ai",         # ASI Alliance rebranded from FET
    "edge":              "edgex",
    "stx":               "blockstack",
    "kite":              "kite-ai",
    "terra-luna-classic": "terra-luna",      # LUNC
    "chz":               "chiliz",
    "sei":               "sei-network",
    "aero":              "aerodrome-finance",
    "tia":               "celestia",
    "sun":               "sun-token",
    "2z":                "doublezero",
    "h":                 "humanity-protocol",
    "xtz":               "tezos",
    "crv":               "curve-dao-token",
    "spx":               "spx6900",
    "zro":               "layerzero",
    "ethfi":             "ether-fi",
    "pyth":              "pyth-network",
    "pendle":            "pendle",
    "btt":               "bittorrent",
    "mon":               "monad-testnet",    # Monad (testnet, may not have full CG entry)
    "gno":               "gnosis",
    "prime":             "echelon-prime",
    "kaia":              "klay-token",       # Kaia (former Klaytn)
    "lit":               "lighter",
    "cfx":               "conflux-token",
    "ldo":               "lido-dao",
    "dcr":               "decred",
    "floki":             "floki",
    "tel":               "telcoin",
    "grt":               "the-graph",
    "nft":               "apenft",
    "op":                "optimism",
    "jasmy":             "jasmycoin",
    "iota":              "iota",
    "strk":              "starknet",
    "ens":               "ethereum-name-service",
    "jto":               "jito-governance-token",
    "grass":             "grass",
    "bill":              "billions-network",
    "xpl":               "plasma-finance",
    "genius":            "genius-token",
    "comp":              "compound-governance-token",
    "ff":                "falcon-finance",
    "ray":               "raydium",
    "axs":               "axie-infinity",
    "neo":               "neo",
    "pieverse":          "pieverse",
    "theta":             "theta-token",
    "wif":               "dogwifcoin",
    "sand":              "the-sandbox",
    "twt":               "trust-wallet-token",
    "sonic":             "sonic-3",          # Sonic (S)
    "ip":                "story-2",          # Story Protocol (IP)
    "mana":              "decentraland",
    "cfg":               "centrifuge",
    "gala":              "gala",
    "wal":               "walrus-2",
    "cvx":               "convex-finance",
    "rune":              "thorchain",
    "eigen":             "eigenlayer",
    "bat":               "basic-attention-token",
    "zk":               "zksync",
    "hnt":               "helium",
    "imx":               "immutable-x",
    "ape":               "apecoin",
    "glm":               "golem",
    "ar":                "arweave",
    "fluid":             "instadapp-fluid",  # corrected 2026-05-25 (was fluid-token)
    "vaulta":            "eos",              # Vaulta is EOS rebranded
    "1inch":             "1inch",
    "ath":               "aethir",
    "dydx":              "dydx-chain",
    "egld":              "elrond-erd-2",
    "kaito":             "kaito",
    "sent":              "sentient",
    "sosovalue":         "sosovalue",
    "zen":               "zencash",
    "safe":              "safe",
    "sahara":            "sahara-ai",
    "lpt":               "livepeer",
    "banana":            "banana-for-scale",
    "rsr":               "reserve-rights-token",
    "snx":               "havven",
    "0g":                "zero-gravity",
    "gas":               "gas",              # NEO Gas
    "bera":              "berachain-bera",
    "linea":             "linea",
    "qtum":              "qtum",
    "kmno":              "kamino",           # corrected 2026-05-25 (was kamino-finance, 404)
    "terra-luna-2":      "terra-luna-2",    # LUNA v2
}

# Assets whose CoinGecko page is known to have no or empty description.
# Included here so we don't waste retry budget.
KNOWN_NO_DESCRIPTION = {
    "cc",       # Canton Network — enterprise chain, sparse CG data
    "night",    # Midnight — pre-mainnet
    "2z",       # DoubleZero — very new
    "h",        # Humanity Protocol — very new
    "bill",     # Billions Network — sparse data
    "xpl",      # Plasma — sparse data
    "genius",   # Genius Token — sparse data
    "ff",       # Falcon Finance — sparse data
    "edge",     # edgeX — sparse data
    "kite",     # Kite AI — sparse data
    "lit",      # Lighter — sparse data
    "pieverse", # Pieverse — sparse data
    "vvv",      # Venice Token — sparse data
    "mon",      # Monad — testnet only
    "sosovalue",# SoSoValue — sparse data
    "aster",    # Aster — post-rename sparse
    "wlfi",     # World Liberty Financial — new
    "pump",     # Pump.fun — meme infrastructure, sparse
    "sahara",   # Sahara AI — pre-mainnet
    "sent",     # Sentient — very new
    "0g",       # 0G — very new
    "vaulta",   # Vaulta (EOS) — rebrand, may be under EOS entry
    "wal",      # Walrus — very new
    "sonic",    # Sonic — may be listed as sonic-3 or sparse
    "ip",       # Story (IP) — very new
}


def strip_html(raw: str) -> str:
    """Remove HTML tags and decode HTML entities from a string."""
    no_tags = re.sub(r"<[^>]+>", " ", raw)
    decoded = html.unescape(no_tags)
    # Collapse whitespace
    return re.sub(r"\s+", " ", decoded).strip()


def first_n_sentences(text: str, n: int = 2) -> str:
    """Return the first n sentences from text."""
    # Split on sentence-ending punctuation followed by whitespace or end
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(sentences[:n]).strip()


def fetch_cg(cg_id: str, timeout: int = 20) -> dict:
    """
    Fetch coin data from CoinGecko. Returns parsed JSON or raises urllib.error.*
    """
    url = (
        f"{CG_BASE}/coins/{cg_id}"
        "?localization=false&tickers=false&community_data=false"
        "&developer_data=false&market_data=false"
    )
    req = request.Request(url, headers={"Accept": "application/json",
                                         "User-Agent": "crypto-sectors/1.1"})
    with request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_with_retry(cg_id: str, asset_id: str) -> dict | None:
    """
    Fetch CG data with exponential backoff. Returns data dict or None on failure.
    """
    for attempt in range(MAX_RETRIES):
        try:
            data = fetch_cg(cg_id)
            return data
        except error.HTTPError as e:
            if e.code == 429:
                wait = BACKOFF_BASE * (2 ** attempt)
                wait = min(wait, 60.0)
                print(f"  [rate-limit] {asset_id}: sleeping {wait:.0f}s (attempt {attempt+1})")
                time.sleep(wait)
            elif e.code == 404:
                print(f"  [404] {asset_id}: cg_id={cg_id} not found on CoinGecko")
                return None
            else:
                print(f"  [HTTP {e.code}] {asset_id}: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(BACKOFF_BASE * (2 ** attempt))
        except Exception as e:
            print(f"  [error] {asset_id}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(BACKOFF_BASE)
    return None


def read_snapshot() -> list[dict]:
    """Read classification/snapshot.csv and return list of row dicts."""
    rows = []
    with open(SNAPSHOT_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def load_existing() -> dict:
    """Load existing descriptions.json assets dict, or empty if file absent."""
    if OUT_JSON.exists():
        with open(OUT_JSON, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("assets", {})
    return {}


def build_output(assets_data: dict, missing: list[str], today: str) -> dict:
    """Build the final JSON structure with sorted keys for stable output."""
    return {
        "schema_version": SCHEMA_VERSION,
        "fetched_at_utc": today,
        "source": SOURCE,
        "attribution_url": ATTRIBUTION_URL,
        "assets": dict(sorted(assets_data.items())),
        "missing": sorted(missing),
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch CoinGecko descriptions for all assets.")
    parser.add_argument("--dry-run", action="store_true", help="Print ids, do not fetch")
    parser.add_argument("--force-refetch", action="store_true",
                        help="Re-fetch even if asset already in existing json")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    rows = read_snapshot()
    existing = load_existing()

    # Today as YYYY-MM-DD; no wall-clock time to keep output stable across reruns
    from datetime import date
    today = date.today().isoformat()

    assets_data = dict(existing)  # start from cache
    missing = []

    print(f"[fetch_descriptions] {len(rows)} assets in snapshot")

    if args.dry_run:
        print("\nDry-run: CoinGecko id mapping would be:")
        for row in rows:
            aid = row["asset_id"]
            cg_id = CG_ID_OVERRIDES.get(aid, aid)
            known_empty = aid in KNOWN_NO_DESCRIPTION
            print(f"  {aid:30s} -> {cg_id}{'  [known-no-desc]' if known_empty else ''}")
        return

    for i, row in enumerate(rows):
        aid = row["asset_id"]
        symbol = row["symbol"]
        cg_id = CG_ID_OVERRIDES.get(aid, aid)

        # Skip if already cached and not forcing refetch
        if aid in assets_data and not args.force_refetch:
            print(f"  [{i+1}/{len(rows)}] {aid}: cached (cg_id={assets_data[aid].get('cg_id', '?')})")
            continue

        if aid in KNOWN_NO_DESCRIPTION:
            print(f"  [{i+1}/{len(rows)}] {aid}: known no-description, skipping fetch")
            assets_data[aid] = {
                "cg_id": cg_id,
                "short_desc": None,
                "long_desc_html_safe": None,
                "fetched_at": today,
                "ok": False,
                "note": "known-sparse-or-pre-mainnet",
            }
            missing.append(aid)
            continue

        print(f"  [{i+1}/{len(rows)}] {aid} ({symbol}) -> cg:{cg_id} ...")

        data = fetch_with_retry(cg_id, aid)

        if data is None:
            print(f"    -> MISSING")
            assets_data[aid] = {
                "cg_id": cg_id,
                "short_desc": None,
                "long_desc_html_safe": None,
                "fetched_at": today,
                "ok": False,
            }
            missing.append(aid)
        else:
            raw_desc = (data.get("description") or {}).get("en") or ""
            if raw_desc:
                clean = strip_html(raw_desc)
                short = first_n_sentences(clean, 2)
                assets_data[aid] = {
                    "cg_id": cg_id,
                    "short_desc": short if short else None,
                    "long_desc_html_safe": clean if clean else None,
                    "fetched_at": today,
                    "ok": True,
                }
                print(f"    -> OK ({len(clean)} chars)")
            else:
                print(f"    -> Empty description on CoinGecko")
                assets_data[aid] = {
                    "cg_id": cg_id,
                    "short_desc": None,
                    "long_desc_html_safe": None,
                    "fetched_at": today,
                    "ok": False,
                    "note": "empty-description-on-coingecko",
                }
                missing.append(aid)

        # Rate-limit sleep (only when we actually made a request)
        if i < len(rows) - 1:
            time.sleep(SLEEP_BETWEEN)

    # Derive missing list from assets_data (ok=False) for completeness
    all_missing = sorted(aid for aid, v in assets_data.items() if not v.get("ok", False))

    out = build_output(assets_data, all_missing, today)

    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, sort_keys=False)
        f.write("\n")

    with open(MISSING_TXT, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# Generated {today}\n")
        f.write(f"# Assets with ok=false in descriptions.json\n")
        for aid in all_missing:
            entry = assets_data.get(aid, {})
            note = entry.get("note", "")
            f.write(f"{aid}  # {note or 'fetch-failed'}\n")

    ok_count = sum(1 for v in assets_data.values() if v.get("ok", False))
    print(f"\n[fetch_descriptions] Done: {ok_count}/{len(rows)} assets got descriptions")
    print(f"  Missing ({len(all_missing)}): {', '.join(all_missing[:10])}{'...' if len(all_missing) > 10 else ''}")
    print(f"  Wrote: {OUT_JSON}")
    print(f"  Wrote: {MISSING_TXT}")


if __name__ == "__main__":
    main()
