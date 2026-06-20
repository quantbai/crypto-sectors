# 加密貨幣 Sector 分類 — 名冊

**232 幣 · 13 個 sector**(9 個 FACTOR、4 個 RESIDUAL)· OKX USDT 本位永續宇宙。

`FACTOR` = 該組展現可與「同規模隨機 null」區分的方向性同向(通過驗證,是真實的軸)。`RESIDUAL` = 經濟上連貫、但未達該門檻的標籤;保留作可解讀的名稱,但在 group-neutralize 時併入市場中性殘差池。詳見 `validation/sector_okx/REPORT.md`。

本檔由 `scripts/build_overview.py` 從 `classification/sector.csv` 自動生成,請勿手動編輯。

---

## 1 · Sector → 幣(全宇宙)

| Sector | 角色 | n | 幣 |
|---|---|--:|---|
| **smart_contract_platform** | 🟢 FACTOR | 45 | 0G, A, ADA, ALGO, APT, AVAX, BERA, CC, CFX, CORE, EGLD, ETC, ETH, FLOW, HBAR, INJ, IOST, IOTA, IP, KITE, LAYER, MERL, MINA, MON, MOVE, NEAR, NEO, NIGHT, ONT, PI, POL, QTUM, RLS, S, SEI, SOL, STX, SUI, TAO, THETA, VANA, XPL, XTZ, ZETA, ZIL |
| **meme** | 🟢 FACTOR | 31 | ACT, BOME, BONK, BRETT, DOGE, FARTCOIN, FLOKI, GIGGLE, HMSTR, JELLYJELLY, MEME, MEW, MOODENG, MUBARAK, NEIRO, NOT, ORDI, PENGU, PEOPLE, PEPE, PIPPIN, PNUT, POPCAT, SATS, SHIB, SPX, TRUMP, TURBO, USELESS, WIF, ZORA |
| **metaverse_gaming** | 🟢 FACTOR | 18 | AGLD, ANIME, APE, AXS, BEAT, BIGTIME, CHZ, DOOD, ENJ, GALA, GMT, IMX, KGEN, MAGIC, MANA, OL, SAND, YGG |
| **eth_scaling** | 🟢 FACTOR | 10 | ARB, CELO, LINEA, METIS, OP, PLUME, SOON, SOPH, STRK, ZK |
| **compute_storage** | 🟢 FACTOR | 9 | AR, ATH, FIL, GLM, GRASS, ICP, LPT, RENDER, WAL |
| **interoperability** | 🟢 FACTOR | 8 | ATOM, BABY, DOT, INIT, KSM, TIA, W, ZRO |
| **value_transfer** | 🟢 FACTOR | 7 | BCH, BTC, LTC, RVN, TRX, XLM, XRP |
| **captive_franchise** | 🟢 FACTOR | 6 | BNB, CRO, ME, NMR, OKB, TON |
| **privacy** | 🟢 FACTOR | 3 | DASH, ZEC, ZEN |
| **defi** | ⚪ RESIDUAL | 52 | 1INCH, AAVE, AERO, AEVO, APR, ASTER, AUCTION, AVNT, BARD, BIO, BLUR, COMP, CRV, CVX, DYDX, EDEN, EIGEN, ENA, ETHFI, GMX, HOME, HUMA, HYPE, JTO, JUP, KMNO, LAB, LDO, LQTY, MET, MMT, MORPHO, ONDO, ORDER, PENDLE, PUMP, RAY, RESOLV, RSR, SKY, SNX, SPK, SUSHI, SYRUP, UNI, VIRTUAL, WET, WLFI, WOO, YB, YFI, ZRX |
| **information_technology** | ⚪ RESIDUAL | 29 | 2Z, ACH, AIXBT, ARKM, BAT, BICO, COAI, ENS, ENSO, GPS, GRT, H, KAITO, LA, MASK, PARTI, PIEVERSE, PROVE, RECALL, SAHARA, SAPIEN, SENT, SHELL, SIGN, SSV, TRUST, WCT, WLD, ZBT |
| **oracles_data** | ⚪ RESIDUAL | 9 | ALLO, API3, AT, BAND, LINK, PYTH, TRB, TRUTH, UMA |
| **OTHER** | ⚪ RESIDUAL | 5 | ETHW, ICX, LRC, LUNA, ONE |

**Sector 定義**

- **smart_contract_platform** — 通用型主權 L1/L2 公鏈,gas/質押(含被當「AI 鏈」行銷、本質仍是 L1 者)
- **meme** — 注意力/社群幣,對持幣者無現金流主張
- **metaverse_gaming** — 遊戲、NFT/IP 品牌、虛擬世界、粉絲代幣
- **eth_scaling** — 結算回 Ethereum 的 Rollup / L2
- **compute_storage** — 去中心化實體資源 DePIN——GPU/算力、儲存、頻寬
- **interoperability** — 跨鏈訊息、橋、模組化 DA、應用鏈樞紐
- **value_transfer** — 貨幣 / 支付結算資產(BTC、XRP、LTC…)
- **captive_franchise** — 單一鏈下營運方營收回購型代幣(交易所/平台/基金/市場)
- **privacy** — 隱私結算鏈
- **defi** — 鏈上金融協議(DEX、借貸、永續、流動性質押、RWA、NFT-fi、launchpad)
- **information_technology** — 鏈上服務/存取/中介(身分、資料服務、access-gating)
- **oracles_data** — 驗證資料餵價 / 預言機網路
- **OTHER** — 非方向性殘差池(殭屍 / 近乎死亡的鏈)

---

## 2 · 各 TOP universe → sector 拆解

每個 tier 是此宇宙內市值前 N 名的幣。下表列出該 tier 橫跨哪些 sector,以及各 sector 收了該 tier 的哪些幣(幣按市值排序)。

### TOP 10  ·  10 幣  ·  5 / 13 個 sector

| Sector | 角色 | # | 幣 |
|---|---|--:|---|
| **value_transfer** | 🟢 FACTOR | 4 | BTC, XRP, TRX, XLM |
| **smart_contract_platform** | 🟢 FACTOR | 3 | ETH, SOL, ADA |
| **meme** | 🟢 FACTOR | 1 | DOGE |
| **captive_franchise** | 🟢 FACTOR | 1 | BNB |
| **defi** | ⚪ RESIDUAL | 1 | HYPE |

### TOP 20  ·  20 幣  ·  5 / 13 個 sector

| Sector | 角色 | # | 幣 |
|---|---|--:|---|
| **smart_contract_platform** | 🟢 FACTOR | 8 | ETH, SOL, ADA, CC, HBAR, SUI, AVAX, NEAR |
| **value_transfer** | 🟢 FACTOR | 6 | BTC, XRP, TRX, XLM, BCH, LTC |
| **meme** | 🟢 FACTOR | 2 | DOGE, SHIB |
| **captive_franchise** | 🟢 FACTOR | 2 | BNB, TON |
| **defi** | ⚪ RESIDUAL | 2 | HYPE, ONDO |

### TOP 30  ·  30 幣  ·  5 / 13 個 sector

| Sector | 角色 | # | 幣 |
|---|---|--:|---|
| **smart_contract_platform** | 🟢 FACTOR | 13 | ETH, SOL, ADA, CC, HBAR, SUI, AVAX, NEAR, ETC, ALGO, POL, APT, NIGHT |
| **value_transfer** | 🟢 FACTOR | 6 | BTC, XRP, TRX, XLM, BCH, LTC |
| **meme** | 🟢 FACTOR | 4 | DOGE, SHIB, PEPE, PENGU |
| **defi** | ⚪ RESIDUAL | 4 | HYPE, ONDO, UNI, MORPHO |
| **captive_franchise** | 🟢 FACTOR | 3 | BNB, TON, OKB |

### TOP 50  ·  50 幣  ·  11 / 13 個 sector

| Sector | 角色 | # | 幣 |
|---|---|--:|---|
| **smart_contract_platform** | 🟢 FACTOR | 16 | ETH, SOL, ADA, CC, HBAR, SUI, AVAX, NEAR, ETC, ALGO, POL, APT, NIGHT, TAO, INJ, SEI |
| **defi** | ⚪ RESIDUAL | 10 | HYPE, ONDO, UNI, MORPHO, AAVE, ENA, JUP, PUMP, VIRTUAL, CRV |
| **value_transfer** | 🟢 FACTOR | 6 | BTC, XRP, TRX, XLM, BCH, LTC |
| **meme** | 🟢 FACTOR | 5 | DOGE, SHIB, PEPE, PENGU, BONK |
| **compute_storage** | 🟢 FACTOR | 3 | ICP, RENDER, FIL |
| **captive_franchise** | 🟢 FACTOR | 3 | BNB, TON, OKB |
| **interoperability** | 🟢 FACTOR | 2 | DOT, ATOM |
| **privacy** | 🟢 FACTOR | 2 | ZEC, DASH |
| **eth_scaling** | 🟢 FACTOR | 1 | ARB |
| **information_technology** | ⚪ RESIDUAL | 1 | WLD |
| **oracles_data** | ⚪ RESIDUAL | 1 | LINK |

### TOP 100  ·  100 幣  ·  12 / 13 個 sector

| Sector | 角色 | # | 幣 |
|---|---|--:|---|
| **smart_contract_platform** | 🟢 FACTOR | 22 | ETH, SOL, ADA, CC, HBAR, SUI, AVAX, NEAR, ETC, ALGO, POL, APT, NIGHT, TAO, INJ, SEI, MON, CFX, IP, BERA, 0G, MOVE |
| **defi** | ⚪ RESIDUAL | 21 | HYPE, ONDO, UNI, MORPHO, AAVE, ENA, JUP, PUMP, VIRTUAL, CRV, ETHFI, JTO, PENDLE, LDO, EIGEN, HOME, DYDX, BIO, SPK, ASTER, BARD |
| **meme** | 🟢 FACTOR | 13 | DOGE, SHIB, PEPE, PENGU, BONK, WIF, FARTCOIN, ORDI, JELLYJELLY, USELESS, TURBO, NOT, PNUT |
| **information_technology** | ⚪ RESIDUAL | 8 | WLD, ENS, PIEVERSE, SENT, KAITO, COAI, ARKM, SAHARA |
| **eth_scaling** | 🟢 FACTOR | 6 | ARB, OP, STRK, ZK, LINEA, SOON |
| **compute_storage** | 🟢 FACTOR | 6 | ICP, RENDER, FIL, GRASS, AR, ATH |
| **value_transfer** | 🟢 FACTOR | 6 | BTC, XRP, TRX, XLM, BCH, LTC |
| **metaverse_gaming** | 🟢 FACTOR | 5 | CHZ, AXS, APE, GALA, ENJ |
| **interoperability** | 🟢 FACTOR | 5 | DOT, ATOM, ZRO, W, BABY |
| **captive_franchise** | 🟢 FACTOR | 3 | BNB, TON, OKB |
| **oracles_data** | ⚪ RESIDUAL | 3 | LINK, PYTH, ALLO |
| **privacy** | 🟢 FACTOR | 2 | ZEC, DASH |

