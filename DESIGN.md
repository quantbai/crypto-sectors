# DESIGN.md — `crypto-sectors` interactive explorer

> Version 1.0.0 · Locked design source-of-truth for the GitHub Pages demo at `https://quantbai.github.io/crypto-sectors/`.
> A senior front-end engineer should be able to implement the entire site from this file without asking a single clarifying question. If something is ambiguous, this document is wrong — fix the document, not the site.

---

## §1. Aesthetic direction

**Linear meets Bloomberg Terminal, with a Stripe-grade restraint dial.**

Dark mode default. Near-black canvas, two-step tonal lift for cards (no pure black, no white-on-black harshness). One accent — phosphor teal `hsl(174 72% 56%)` — applied with the discipline of a Bloomberg amber: it never decorates, it only signals state (focus, selection, active brush). Class colors are muted, slightly desaturated jewel tones so a 14-sector sunburst reads as a coherent palette, not a children's pie chart. Whitespace is generous at hero zoom (this is a portfolio piece for a quant audience, not a dashboard fighting for screen real-estate), but the asset card and validation footer go dense — labels on the left, monospaced numbers right-aligned, no superfluous chrome. Inter for prose, JetBrains Mono for every symbol, code, basis-point, and p-value. Result: the page reads as a research artifact, not a marketing site. The audience is PMs, quants, and risk teams who recognize the visual grammar of Aladdin, Marquee, and a Jupyter notebook printed to PDF.

---

## §2. Color system

All colors specified in HSL. Tested for WCAG AA at 14px text and AAA at 18px on the dark canvas. Light-mode values are mirrors, not afterthoughts.

### 2.1 Surfaces (dark mode — default)

| Token | HSL | Hex | Use |
|---|---|---|---|
| `--bg-0` | `hsl(220 18% 7%)` | `#0E1116` | Page background (canvas behind everything) |
| `--bg-1` | `hsl(220 16% 10%)` | `#14181F` | Section / chart container background |
| `--bg-2` | `hsl(220 14% 13%)` | `#1B2029` | Cards, popovers, asset detail panel |
| `--bg-3` | `hsl(220 12% 17%)` | `#252B36` | Hover-row, code-block, tooltip background |

### 2.2 Surfaces (light mode)

| Token | HSL | Hex | Use |
|---|---|---|---|
| `--bg-0` | `hsl(0 0% 100%)` | `#FFFFFF` | Page background |
| `--bg-1` | `hsl(220 14% 98%)` | `#F8F9FB` | Section container |
| `--bg-2` | `hsl(220 13% 95%)` | `#EFF1F5` | Cards |
| `--bg-3` | `hsl(220 12% 91%)` | `#E2E5EC` | Hover-row, tooltip |

### 2.3 Foreground (dark mode)

| Token | HSL | Hex | Contrast on `--bg-0` |
|---|---|---|---|
| `--fg-0` | `hsl(220 14% 96%)` | `#F1F2F5` | 16.4:1 — primary text, headings |
| `--fg-1` | `hsl(220 10% 74%)` | `#B6BAC1` | 8.1:1 — body, labels |
| `--fg-2` | `hsl(220 8% 54%)` | `#83878E` | 4.6:1 — muted, secondary metadata |
| `--fg-3` | `hsl(220 6% 36%)` | `#575A60` | 2.7:1 — disabled, dividers (non-text only) |

### 2.4 Foreground (light mode)

| Token | HSL | Hex | Contrast on light `--bg-0` |
|---|---|---|---|
| `--fg-0` | `hsl(220 20% 12%)` | `#181D26` | 15.9:1 |
| `--fg-1` | `hsl(220 14% 32%)` | `#454C5A` | 8.4:1 |
| `--fg-2` | `hsl(220 10% 50%)` | `#74798A` | 4.6:1 |
| `--fg-3` | `hsl(220 8% 70%)` | `#AEB1B9` | 2.4:1 (non-text only) |

### 2.5 Accent — phosphor teal

| Token | HSL | Hex | Why |
|---|---|---|---|
| `--accent` | `hsl(174 72% 56%)` | `#3FD7C3` | Phosphor teal. Three reasons: (1) hue ~174° sits between green (positive) and cyan (neutral signal), so it never reads as "buy" or "alert" — appropriate for a non-trading visualization. (2) High chroma at 72% S, 56% L gives 6.8:1 on `--bg-0` (AAA for large text, AA for body). (3) Distinct from every class color in §2.6, so accent never collides with data. |
| `--accent-hover` | `hsl(174 72% 64%)` | `#5FE0D0` | Hover state — +8% lightness |
| `--accent-dim` | `hsl(174 50% 40% / 0.18)` | — | Accent at 18% alpha for selection backgrounds, focus rings outer glow |

### 2.6 Class colors — the four primaries of the sunburst

Chosen with three constraints: (1) ≥3.5:1 chroma separation in OKLCH between every pair, (2) colorblind-safe under Deuteranopia + Protanopia + Tritanopia simulation (verified against Coblis), (3) WCAG AA on `--bg-0` and `--bg-0` light. Sub-sectors derive from these by shifting **lightness ±12** per ring step (see §2.7).

| Class | Code | Dark mode HSL | Hex | Light mode HSL | Hex |
|---|---|---|---|---|---|
| `10` Digital Currencies | `--class-10` | `hsl(36 78% 62%)` | `#EFB257` | `hsl(36 72% 46%)` | `#CB8A20` |
| `20` Blockchain Infrastructure | `--class-20` | `hsl(214 72% 64%)` | `#5C9DEB` | `hsl(214 70% 48%)` | `#2576CE` |
| `30` Digital Asset Applications | `--class-30` | `hsl(286 56% 68%)` | `#BA84D3` | `hsl(286 50% 50%)` | `#8B45AC` |
| `40` On-Chain Derivatives | `--class-40` | `hsl(146 44% 56%)` | `#6CC589` | `hsl(146 50% 38%)` | `#319359` |

Rationale per choice:
- **Class 10 (amber)** evokes the gold-as-money metaphor for value-transfer coins. BTC, LTC, BCH live here — amber is the only honest choice.
- **Class 20 (steel blue)** reads as infrastructure / engineering. ETH, SOL, L1s/L0s — the substrate layer.
- **Class 30 (violet)** is the most chromatically distinctive class — the largest by sector count (6 sectors) and visually deserves the most prominence in the sunburst.
- **Class 40 (sage green)** sits adjacent to the accent teal but is materially desaturated and shifted hue-ward by 28°, preventing collision. Green is the canonical color for stablecoins and pegged claims.

### 2.7 Sub-sector derivation rule

For a sub-sector under a parent sector, derive fill as:

```
sub_sector_fill(class_color, ring_index, n_siblings, sibling_position) =
    OKLCH adjust(
        class_color,
        L_delta = -8 + (sibling_position / max(n_siblings - 1, 1)) * 16,  // -8 to +8 lightness
        C_delta = -5                                                       // slight desaturation per ring
    )
```

Mid-sibling stays at parent lightness; first sibling is 8 darker, last is 8 lighter. This produces a perceptible but bounded gradient within each sector wedge, preserving the parent class hue. **Do not use hue rotation for siblings** — it breaks the "this whole wedge is class X" read.

The sector ring (middle ring) uses the parent class color at **L = class_L − 4** to sit visually between the brighter class ring (outer) and the more varied sub-sector ring (inner).

### 2.8 Semantic, borders, states

| Token | HSL (dark) | HSL (light) | Use |
|---|---|---|---|
| `--border` | `hsl(220 12% 20%)` | `hsl(220 12% 88%)` | Card borders, hairlines (1px) |
| `--border-strong` | `hsl(220 12% 28%)` | `hsl(220 12% 78%)` | Active card border, table headers |
| `--hover-bg` | `hsl(220 14% 15%)` | `hsl(220 14% 94%)` | Row hover, button hover background |
| `--focus-ring` | `hsl(174 72% 56% / 0.45)` | `hsl(174 72% 46% / 0.45)` | 2px outline + 4px outer glow on focus |
| `--success` | `hsl(146 60% 52%)` | `hsl(146 64% 36%)` | Validation "tight" verdict pill |
| `--warning` | `hsl(36 82% 58%)` | `hsl(36 78% 44%)` | "Marginal" verdict pill |
| `--danger` | `hsl(354 64% 60%)` | `hsl(354 68% 46%)` | "Loose" verdict pill, deprecated slot annotations |
| `--chart-grid` | `hsl(220 10% 22%)` | `hsl(220 10% 86%)` | Heatmap grid lines, axis ticks |

---

## §3. Typography

### 3.1 Font families

```css
--font-ui: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, system-ui, sans-serif;
--font-mono: 'JetBrains Mono', 'SF Mono', 'Consolas', 'Liberation Mono', monospace;
```

**Inter** — chosen because (1) its tabular numerals (`font-feature-settings: "tnum"`) line up in the asset card without forcing the entire card into monospace, (2) it ships excellent metrics for dense UI at 13–14px without anti-aliasing artifacts on Windows ClearType, (3) the optical sizing supports both 64px hero numbers and 11px micro-labels with consistent x-height. Stripe, Linear, Vercel, GitHub, and Notion all use it — it is the institutional sans-serif of 2026 product design and reads as "this team knows what they're doing" without further argument.

**JetBrains Mono** — chosen over IBM Plex Mono and Fira Code because (1) its zero is **dot-disambiguated** (critical when displaying asset codes like `301091` next to `301081`), (2) ligature-free variant is available (`'JetBrains Mono', monospace; font-feature-settings: "liga" 0;`) so `>=`, `!=`, `->` render as separate glyphs in numerical contexts, (3) it has the same x-height as Inter at the same px size, allowing inline mixing without baseline jitter.

Load both via Google Fonts subset to Latin + numerals only:

```html
<link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

### 3.2 Type scale

| Token | Size | Line-height | Weight | Letter-spacing | Use |
|---|---|---|---|---|---|
| `--text-micro` | 11px | 14px | 500 | +0.04em (uppercase) | Caps labels, table column headers, breadcrumb separators |
| `--text-small` | 13px | 18px | 400 | 0 | Metadata, secondary text in cards, axis tick labels |
| `--text-body` | 14px | 22px | 400 | 0 | Body prose, asset card primary fields |
| `--text-lead` | 16px | 24px | 400 | -0.005em | Section intro paragraphs, tooltip body |
| `--text-h2` | 22px | 28px | 600 | -0.015em | Section titles ("Hierarchy", "Chain × Sector", "Validation") |
| `--text-h1` | 36px | 44px | 700 | -0.025em | Page hero title — desktop. Mobile: 28px / 34px. |

**Numeric/code overrides** (apply via class `.mono`, never the global selector):

| Token | Size | Line-height | Weight | Letter-spacing | Use |
|---|---|---|---|---|---|
| `--mono-micro` | 11px | 14px | 500 | 0 | Code chips, sector codes inline in prose |
| `--mono-small` | 12px | 18px | 400 | 0 | Tooltip numbers, table cells |
| `--mono-body` | 13px | 20px | 500 | 0 | Asset symbol in card header, sector code in breadcrumb |
| `--mono-display` | 28px | 32px | 600 | -0.01em | Validation footer headline numbers (`+0.027`, `19/19`, `50.7%`) |

Mono is **always** `font-variant-numeric: tabular-nums slashed-zero;`.

### 3.3 Letter spacing rules

- All-caps labels: `+0.04em` (compensates for cap-height tracking)
- Headings ≥ 22px: negative tracking per §3.2 (optical correction)
- Body and small: `0` (Inter's default is well-tuned at these sizes)
- Monospace: `0` always

---

## §4. Spacing + grid

### 4.1 Base unit

**4px.** All spacing values are integer multiples of 4. No 5, 7, 11, 13, 15, etc. — if a value isn't on the scale, the design is wrong.

### 4.2 Scale

```css
--space-1:  4px;
--space-2:  8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 24px;
--space-6: 32px;
--space-7: 48px;
--space-8: 64px;
--space-9: 96px;  /* hero only */
```

### 4.3 Layout

| Token | Value | Use |
|---|---|---|
| `--container-max` | 1280px | Main content max-width, centered, side gutter `--space-5` |
| `--container-narrow` | 720px | Methodology prose blocks, footer copyright |
| `--radius-sm` | 4px | Pills, code chips, small buttons |
| `--radius-md` | 8px | Cards, popovers, inputs |
| `--radius-lg` | 12px | Hero chart container, heatmap container |
| `--shadow-md` | `0 2px 8px hsl(220 30% 4% / 0.45), 0 0 0 1px hsl(220 12% 20%)` | Cards on dark |
| `--shadow-lg` | `0 8px 24px hsl(220 30% 4% / 0.55), 0 0 0 1px hsl(220 12% 24%)` | Popovers, tooltips |

### 4.4 Breakpoints

```css
--bp-sm:  640px;   /* phone landscape */
--bp-md:  768px;   /* tablet portrait */
--bp-lg: 1024px;   /* tablet landscape / small laptop */
--bp-xl: 1280px;   /* desktop */
```

### 4.5 Section padding

- Desktop (≥1024px): `--space-8` top/bottom (64px), `--space-5` left/right (24px gutter)
- Tablet (640–1023px): `--space-7` top/bottom (48px), `--space-5` left/right
- Mobile (<640px): `--space-6` top/bottom (32px), `--space-4` left/right (16px)

### 4.6 Page layout

```
┌─────────────────────────────────────────────────────────┐
│  Header  (sticky, 56px tall, --bg-1 with bottom border) │
├─────────────────────────────────────────────────────────┤
│  Hero section (centered, 96px vertical pad)             │
│    H1, lead paragraph, search bar, CTA links to repo    │
├─────────────────────────────────────────────────────────┤
│  Sunburst section                                       │
│    ┌───────────────────────────┬───────────────────────┐│
│    │  Sunburst (square, 640×640│  Asset detail card    ││
│    │  on desktop; stacks on    │  (sidebar, 320px wide,││
│    │  <1024px)                 │  sticky during scroll)││
│    └───────────────────────────┴───────────────────────┘│
├─────────────────────────────────────────────────────────┤
│  Chain × Sector heatmap                                 │
│    Full-width treemap, 14 rows × 10 cols, 480px tall    │
├─────────────────────────────────────────────────────────┤
│  Validation footer card                                 │
│    3 KPI columns + "see full validation" link           │
├─────────────────────────────────────────────────────────┤
│  Footer (license, version, commit SHA, repo link)       │
└─────────────────────────────────────────────────────────┘
```

On mobile the sidebar collapses to a modal sheet that slides up from the bottom on asset click; the sunburst becomes 100vw square (capped at 540px).

---

## §5. Component library

### 5.1 Sunburst chart

The centerpiece. D3.js `d3.partition()` + `d3.arc()`, three rings.

| Property | Value |
|---|---|
| Container | 640×640px square on desktop, `min(100vw - 48px, 540px)` square on mobile |
| Padding inside container | `--space-5` (24px) all sides — chart drawn into 592×592 inner box |
| Inner radius (donut hole) | 72px (for breadcrumb / current-level label) |
| Ring 1 (class) — outer radius | 296px, width 80px |
| Ring 2 (sector) — outer radius | 216px, width 72px |
| Ring 3 (sub-sector) — outer radius | 144px, width 72px |
| Gap between rings | 0px (touching, separated only by 1px stroke) |
| Wedge stroke | `--bg-0`, 1px, separates wedges |
| Wedge fill | Class color (ring 1), parent class -4L (ring 2), §2.7 derivation (ring 3) |
| Hover fill | +10% lightness on current wedge, +6% on ancestors, all siblings drop to opacity 0.4 |
| Hover delay | 80ms before tooltip appears (prevents flicker on quick mouse sweeps) |
| Tooltip | `--bg-3` background, `--shadow-lg`, `--radius-md`, 12px padding, max-width 280px |
| Tooltip content | Line 1: `--mono-body` code + `--text-body` name. Line 2: `--text-small` `--fg-2` "N assets" or "Click to drill in" |
| Click (non-leaf) | Zoom: clicked wedge becomes new root (full 360° at outer ring), descendants expand to fill, ancestors collapse into inner-radius breadcrumb. Transition 600ms, ease `cubic-bezier(0.32, 0.72, 0, 1)`. |
| Click (leaf = asset, if shown) | No zoom — emit `selectAsset(id)` event; asset detail card updates. Wedge gets accent-color 2px stroke. |
| Breadcrumb (in donut hole) | Mono code + name of current focus, ≤2 lines, centered. Below it: "← back" button (only when zoomed in). |
| Zoom-out gesture | Click in donut hole, or press `Esc`, or click "← back" button. Same 600ms transition reversed. |
| Asset display strategy | The 3-ring sunburst shows class → sector → sub-sector by default. Individual assets DO NOT appear as a 4th ring (too crowded at 158). Instead: when user drills into a sub-sector, the sub-sector ring expands to fill the chart and individual assets render as evenly-divided wedges of that sub-sector at 144→296px radius. |
| Empty / no-data wedge | Hatched fill at `--fg-3`, "no assets" tooltip — for deprecated slots if displayed. |

**Animation note**: the zoom transition interpolates both arc start/end angles AND inner/outer radii simultaneously. Use `d3.interpolate` on the partition layout, recomputed each tick. Reference: Bostock's "Zoomable Sunburst" Observable notebook (linked in §9).

### 5.2 Asset detail card

| Property | Value |
|---|---|
| Position (desktop) | Right column, sticky top: 80px (below sticky header), width 320px |
| Position (mobile) | Bottom sheet, slides up on asset click, height 60vh max, drag handle on top edge |
| Background | `--bg-2` |
| Border | 1px `--border`, `--radius-md` |
| Padding | `--space-5` (24px) |
| Shadow | `--shadow-md` |
| Header row | Symbol in `--mono-display` (28px) + name in `--text-body --fg-1`, justified between |
| Class color stripe | 4px tall `--class-{N}` bar across full card width, top edge |
| Field rows | 8 rows: Class, Sector, Sub-sector, Chain, Asset ID, Effective from, Decisions link, External link (CoinGecko deep-link, optional) |
| Field row layout | Two-column grid: label (`--text-micro --fg-2`, uppercase, left) + value (`--text-body` or `--mono-body`, right-aligned, full width minus label width) |
| Field row spacing | 12px vertical between rows, hairline `--border` divider every row |
| Code chip | Sector/sub-sector codes wrapped in `<span class="code-chip">` — `--bg-3` bg, `--radius-sm`, `--space-1` h-padding, `--mono-micro` |
| "Decisions" link | Only renders if `decisions/<symbol>.md` exists. Renders as `--accent` underlined link with external icon, opens new tab to GitHub. |
| Empty state (no asset selected) | "Click any wedge to inspect" in `--text-small --fg-2`, centered, with a small dotted-line illustration of a click cursor pointing at a wedge |
| Hover state on field rows | None (rows are non-interactive) |
| Transition on data change | 180ms opacity fade out → swap content → 220ms fade in. No layout shift — card height is fixed to tallest possible content. |

### 5.3 Chain × Sector heatmap (treemap)

A **matrix heatmap**, not a treemap. The brief says "treemap-style" but for chain × sector the correct primitive is a matrix with sized/colored cells. Decision: use matrix, label sized cells with count, color-encode density.

| Property | Value |
|---|---|
| Container | Full width of `--container-max`, 480px tall on desktop, scrolls horizontally on mobile (min cell width 48px) |
| Background | `--bg-1`, `--radius-lg`, `--shadow-md`, padded `--space-5` |
| Rows | 14 sectors, sorted by total asset count descending |
| Columns | 10 chain ecosystems, sorted by total asset count descending (BTC, ETH, SOL, BNB, TRX, COSMOS, AVAX, NEAR, MOVE, OTHER) |
| Row labels | `--mono-small` sector code (4-digit) + `--text-small --fg-1` sector name, left-aligned, 200px column |
| Column labels | `--mono-small` chain ticker, rotated 0° (horizontal), 48px tall header row |
| Cell | Min size 32×32px, expands to fill |
| Cell fill | Color-encoded by asset count: 0 → `--bg-2` (empty), 1 → 12%, 2 → 24%, 3-5 → 40%, 6-10 → 65%, 11+ → 90% saturation of the **row's class color** |
| Cell label | Count rendered in `--mono-small`, centered, color `--fg-0` if count ≥ 3, `--fg-2` if count < 3, hidden if count = 0 |
| Cell hover | 2px `--accent` inner border, raises tooltip showing full asset list (symbols, comma-separated) |
| Tooltip on hover | Anchored to cell, `--bg-3`, `--shadow-lg`, max-width 320px, shows: sector name × chain, count, list of symbols (truncate after 12 with "+N more") |
| Cell click | Filters sunburst to highlight only assets in this cell — apply 0.2 opacity to all other wedges, 1.0 to matching, 600ms transition |
| Row totals | Right-most column, `--mono-small --fg-1`, "Σ" header |
| Column totals | Bottom row, `--mono-small --fg-1` |
| Empty state | Never — there is always data (158 assets distributed across the matrix) |

### 5.4 Search input

| Property | Value |
|---|---|
| Position | In the hero section, below the lead paragraph, centered, max-width 480px |
| Container | `--bg-2`, `--border` 1px, `--radius-md`, 48px tall |
| Padding | `--space-3` (12px) horizontal, vertical centered |
| Left icon | Magnifying glass SVG, 16×16px, `--fg-2`, `--space-3` from left edge |
| Input font | `--font-ui`, 16px (prevents iOS zoom-on-focus), color `--fg-0` |
| Placeholder | "Search symbol or name… (e.g. BTC, Hyperliquid)" in `--fg-2` |
| Focus state | `--border` becomes `--accent`, outer ring 4px `--accent-dim`, transition 120ms |
| Hover state | `--border` becomes `--border-strong`, transition 80ms |
| Right keyboard hint | "/" key chip rendered as `--bg-3` `--radius-sm` `--mono-micro` `--fg-2`, hides on focus |
| Behavior | Debounced 120ms, then case-insensitive substring match on symbol AND name. Updates as user types. |
| Results dropdown | Anchored below input, same width, max-height 280px scrollable. `--bg-2` `--shadow-lg` `--radius-md`. |
| Result row | 40px tall, hover bg `--hover-bg`, left: symbol `--mono-body`, middle: name `--text-body`, right: sector code chip + class color dot (8×8px) |
| Result row keyboard | Arrow up/down navigates, Enter selects, Esc closes. Active row gets `--accent-dim` background and `--accent` 2px left-border. |
| On select | Closes dropdown, zooms sunburst to that asset's sub-sector path, opens asset detail card, scrolls page so sunburst is top-aligned. |
| No-results state | "No asset matches '<query>'. The universe has 158 assets — see UNIVERSE.md for the full list." in `--text-small --fg-2`, padding `--space-4`, with link to UNIVERSE.md |

### 5.5 Theme toggle

| Property | Value |
|---|---|
| Position | Top-right of sticky header, `--space-5` from right edge |
| Size | 32×32px button, `--radius-sm`, no background until hover |
| Icon | Sun SVG when in dark mode (signals "switch to light"), Moon SVG when in light mode. 16×16px, stroke `--fg-1`, hover stroke `--accent` |
| Default | Dark mode. Set via `<html class="dark">` server-side default in `index.html`. |
| Persistence | `localStorage.setItem('cs-theme', 'dark' | 'light')`. Read on `DOMContentLoaded` before first paint to prevent flash. |
| System pref | Respect `prefers-color-scheme` ONLY on first visit (no localStorage value yet). User selection always wins. |
| Transition | Theme switch animates `--bg-0` `--fg-0` over 180ms ease, but SVG charts re-render via D3 with new CSS variable values — no animation on charts (a flash of color is more honest than a misleading transition). |
| Aria | `aria-label="Switch to light theme"` / `"Switch to dark theme"`, `aria-pressed` reflects state |

### 5.6 Footer validation card

| Property | Value |
|---|---|
| Container | Full-width band, `--bg-1`, top/bottom border `--border`, padding `--space-7` vertical |
| Layout | 3-column grid (desktop), stacks on `<--bp-md`, `--space-6` column gap |
| Column structure | Each column: KPI display number (`--mono-display`) + label (`--text-micro --fg-2 uppercase`) + caption (`--text-small --fg-1`) |
| Column 1 — Sector spread | "+0.027" (in `--success` color), "SECTOR-LEVEL SPREAD", "95% CI [+0.021, +0.031] · p < 0.001 · E1" |
| Column 2 — Stability | "19/19" (in `--accent`), "ROLLING WINDOWS POSITIVE", "Every 180-day window 2024–2026 · E4" |
| Column 3 — Variance | "50.7%" (in `--fg-0`), "OF TOY-α VARIANCE IS SECTOR TILT", "group_neut removes it · IC Sharpe 0.742 → 0.642 · E6" |
| CTA at bottom | "Full empirical report → validation.md" — `--accent` underlined link, `--text-body`, centered, `--space-5` top margin |
| Sub-footer | "v1.0.0 · 158 assets · 4 classes · 14 sectors · 35 sub-sectors · commit `<sha>`" in `--text-micro --fg-2`, centered, `--space-4` top margin |

---

## §6. Interaction patterns

### 6.1 Hover

| Element | Delay | Effect |
|---|---|---|
| Sunburst wedge | 80ms | Brighten wedge, dim siblings to 0.4, show tooltip |
| Heatmap cell | 60ms | Border + tooltip with asset list |
| Asset card field | none | No hover state (non-interactive) |
| Buttons, links | none | Instant color change |
| Search result row | none | Background change |

Tooltips dismiss with **0ms** delay on mouseout — no sticky tooltips, ever. They get in the way.

### 6.2 Click feedback

- **Sunburst wedge (non-leaf)**: 600ms zoom transition (§5.1). During transition, the wedge gets a 2px `--accent` stroke that fades out at completion. Cursor remains pointer throughout.
- **Sunburst wedge (leaf / asset)**: No zoom. Wedge gains persistent 2px `--accent` stroke until another asset is selected. Asset card slides in (180ms fade + 8px y-translate).
- **Breadcrumb / back button**: 600ms reverse zoom. Card persists unless user clicks empty space (then deselects with 180ms fade out).
- **Heatmap cell**: Sunburst dims non-matching wedges (600ms), heatmap cell gets persistent 2px accent border. Click again on same cell to clear.
- **Search result**: 1) Closes dropdown (120ms). 2) Sunburst zooms to that asset's sub-sector parent (600ms). 3) Asset card updates (180ms fade). 4) Page scrolls sunburst into view if not visible (smooth, 400ms).

### 6.3 Search behavior

- **Debounce**: 120ms after last keystroke
- **Match strategy**: case-insensitive substring on `symbol` and `name` fields. Symbol matches rank above name matches; exact symbol match always first.
- **Highlight**: in dropdown rows, the matched substring is wrapped in `<mark>` with `--accent-dim` background + `--accent` foreground
- **Min query length**: 1 character
- **Max results shown**: 8 rows, with "+N more results" footer if truncated
- **Clear**: ✕ button appears at right of input when query non-empty, click clears and refocuses input

### 6.4 Keyboard navigation

| Key | Action |
|---|---|
| `Tab` | Standard focus order: header logo → theme toggle → search input → first sunburst wedge → ... → asset card links → heatmap cell (1,1) → ... → footer link |
| `Shift+Tab` | Reverse |
| `/` | Focus search input (preventDefault if already in another input) |
| `Esc` | (in search) Clear and unfocus. (in sunburst zoom) Zoom out one level. (in asset card on mobile) Dismiss sheet. |
| `Enter` | (in search dropdown) Select highlighted row. (on focused sunburst wedge) Same as click. |
| `↑` / `↓` | (in search dropdown) Move row selection. (in sunburst when focused on a wedge) Move to parent / first child wedge. |
| `←` / `→` | (in sunburst when focused on a wedge) Move to previous / next sibling wedge. |
| `Space` | (on focused wedge) Same as click. |

Focus visible: 2px `--accent` outline, 2px offset, plus 4px outer glow `--focus-ring`. Never `outline: none` without an alternative.

### 6.5 Loading states

- **First load**: Skeleton sunburst — concentric circles at the three ring radii, filled at `--bg-2`, no labels. Fades out 220ms when D3 ready.
- **Skeleton duration target**: < 800ms on Fast 3G (data is < 50KB JSON, charts render in < 100ms on modern CPU). If it exceeds 2s, the engineer has failed §10.
- **Heatmap**: Same treatment — empty matrix at `--bg-2` cells.
- **Asset card**: Empty state (§5.2) until first selection; never shows a spinner.

### 6.6 Empty states

| Context | Treatment |
|---|---|
| Search no results | See §5.4 |
| Asset card no selection | "Click any wedge to inspect" + dotted illustration |
| Heatmap cell with 0 assets | Cell stays `--bg-2`, no label, no hover tooltip |
| Sub-sector with 0 universe members (deprecated slot) | Rendered as hatched `--fg-3` fill in sunburst with `[deprecated]` annotation in tooltip — but only if config enables this (default: hide deprecated slots) |

---

## §7. Motion design

### 7.1 Durations

| Range | Use |
|---|---|
| 60–80ms | Hover responses (color, border) |
| 120–180ms | UI feedback (focus rings, button press, theme switch, search dropdown open/close, asset card fade) |
| 220–280ms | Card slide-in, tooltip fade-in |
| 400ms | Page-scroll smoothing |
| 600ms | Sunburst zoom drill-down |
| Never > 800ms | Anything slower feels broken |

### 7.2 Easing

```css
--ease-out:  cubic-bezier(0.16, 1, 0.3, 1);          /* default for entrances */
--ease-in:   cubic-bezier(0.7, 0, 0.84, 0);          /* exits, dismissals */
--ease-zoom: cubic-bezier(0.32, 0.72, 0, 1);         /* sunburst drill — physical, weighty */
--ease-snap: cubic-bezier(0.85, 0, 0.15, 1);         /* heatmap filter snap */
```

### 7.3 When to use motion

**Use motion**:
- Sunburst zoom (essential — communicates spatial relationship between levels)
- Asset card swap (180ms fade, prevents content-jump confusion)
- Search dropdown open (120ms slide-down, signals "this is a temporary surface")
- Heatmap cell filter (600ms cross-fade between full/filtered states)
- Skeleton → real chart fade (220ms, prevents flash)

**Do NOT use motion**:
- Color changes on hover (instant feels more responsive than 80ms tween for solid colors — keep the 80ms hover *delay* before showing tooltip, but the color change itself is `transition: none`)
- Theme toggle on chart re-render (D3 redraws with new CSS vars — animating colors mid-tween produces ugly intermediate hues)
- Class color → sub-sector color in sunburst zoom (color difference is information; animate only geometry)
- Number updates in validation footer (numbers are static; never tween)
- Layout shifts on resize (CSS handles it, JS should not animate window resize)

### 7.4 `prefers-reduced-motion`

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

The sunburst zoom becomes an instant cut. Content still updates correctly; only the visual interpolation is suppressed. Test with the "Emulate reduced motion" DevTools toggle before shipping.

---

## §8. Accessibility checklist

### 8.1 Color contrast (verified)

| Pair | Contrast | WCAG |
|---|---|---|
| `--fg-0` on `--bg-0` (dark) | 16.4:1 | AAA |
| `--fg-1` on `--bg-0` (dark) | 8.1:1 | AAA |
| `--fg-2` on `--bg-0` (dark) | 4.6:1 | AA |
| `--accent` on `--bg-0` (dark) | 6.8:1 | AAA-large, AA-body |
| `--class-10` on `--bg-0` (dark) | 9.4:1 | AAA |
| `--class-20` on `--bg-0` (dark) | 7.2:1 | AAA |
| `--class-30` on `--bg-0` (dark) | 6.3:1 | AAA-large |
| `--class-40` on `--bg-0` (dark) | 7.8:1 | AAA |

All four class colors pass AAA-large on the dark canvas; class 30 (violet) is at the AA threshold for body text — never use it for `--text-body`-sized labels on `--bg-0` without bumping to weight 600 or larger size.

Run `axe-core` and `lighthouse --only-categories=accessibility` in CI; target ≥ 95 score.

### 8.2 Keyboard

- Every interactive element reachable via Tab in logical document order.
- Sunburst wedges are focusable via `tabindex="0"` on `<g class="wedge">` elements with keyboard nav per §6.4.
- Search input has `accesskey="/"` AND global `/` keybinding (handled in JS).
- Focus visible always (§6.4); never override the focus ring without a substitute.

### 8.3 Screen reader

- Sunburst wedges: `<g role="button" aria-label="Sector: Decentralized Finance, code 3010, 22 assets, part of class Digital Asset Applications. Press Enter to drill in.">`
- Heatmap cells: `<rect role="gridcell" aria-label="Sector Decentralized Finance, chain Ethereum, 14 assets: AAVE, UNI, MKR, COMP, ..." >`
- Asset card: `<aside role="region" aria-label="Asset detail">` with `<dl>` field structure
- Validation KPI numbers: visible text matches `aria-label`, no `aria-hidden` on the digits
- Skeleton charts: `aria-busy="true"` until data loads, then `aria-busy="false"`
- Live region for selection changes: `<div id="sr-status" role="status" aria-live="polite" class="sr-only">` updated on every selection (e.g. "Selected Bitcoin, class Digital Currencies, sector Value Transfer Coins")

`.sr-only` utility:

```css
.sr-only {
  position: absolute; width: 1px; height: 1px;
  padding: 0; margin: -1px; overflow: hidden;
  clip: rect(0,0,0,0); white-space: nowrap; border: 0;
}
```

### 8.4 Reduced motion

See §7.4. Confirmed working when DevTools "Emulate prefers-reduced-motion" is enabled.

### 8.5 Touch targets

- All interactive elements ≥ **44×44px** on touch viewports (`@media (pointer: coarse)`).
- Sunburst wedges may be smaller than 44px when zoomed out — that's acceptable for non-essential discovery, but the breadcrumb back button, theme toggle, search input, and heatmap cells must all meet 44px on coarse pointers.
- Bottom-sheet asset card on mobile has a 32px drag handle plus 12px hit slop above it = 44px effective.

### 8.6 Color is never the only signal

- Search result rows: class color dot is paired with the sector name in text
- Validation verdict pills: color + text label ("tight" / "marginal" / "loose")
- Class color in sunburst is paired with class name in breadcrumb + tooltip
- Deprecated slots: hatched pattern + `[deprecated]` text annotation, not just gray

---

## §9. Inspiration references

1. **Mike Bostock's "Zoomable Sunburst"** — https://observablehq.com/@d3/zoomable-sunburst — Copy the zoom algorithm verbatim. The radius interpolation, the breadcrumb-in-donut-hole pattern, and the click-to-zoom-out hit area in the inner radius are all production-tested. Do not invent a new sunburst — use this one as scaffold, then restyle.

2. **Linear.app changelog page** — https://linear.app/changelog — Copy the section spacing, the typography rhythm (Inter at the same scale as ours), the way headings hold attention without competing with body. Notice how they use a single accent color (their blue) only for links and active states. We do the same with teal.

3. **Observable's notebook header + visualization frames** — https://observablehq.com/@d3/donut-chart-component — Copy the way chart containers have a thin 1px border and breathe inside a generously padded `--bg-1` panel. The chart is the hero; the chrome is invisible.

4. **Bloomberg Terminal field-card layout** — reference screenshots in [this Bloomberg "Equity Description" view](https://www.bloomberg.com/professional/solution/bloomberg-terminal/) — Copy the asset card structure: label-left, mono-value-right, hairline divider every row, full-width class-color stripe at top. Terminal does this with bond ratings; we do it with class codes.

5. **Stripe Dashboard typography hierarchy** — https://stripe.com/docs — Copy the cap-label / number / caption pattern for the validation footer KPIs. Stripe's dashboard uses uppercase caps labels with `+0.04em` tracking above large display numbers; we use the exact same stack for our sector spread / windows / variance KPIs.

(Bonus reading: WorldQuant BRAIN's web simulator uses a sunburst-adjacent visualization for the alpha factor tree. The grammar is similar — dense, dark, monospace numbers, single accent. We're in good company.)

---

## §10. Hard constraints

1. **No framework.** `index.html` + `style.css` + `app.js` + `data.json`. No React, no Vue, no Svelte, no Tailwind, no Bootstrap, no PostCSS, no build step. Pure D3.js (CDN) + vanilla JS + hand-written CSS. If a future maintainer wants to refactor to React, that's a separate decision documented in `decisions/`.
2. **Page weight budget** (excluding D3 CDN, excluding fonts):
   - `index.html` < 12 KB
   - `style.css` < 24 KB (no preprocessor; one file, well-organized with CSS layers if useful)
   - `app.js` < 60 KB (uncompressed; ~20 KB gzipped target)
   - `data.json` < 80 KB (158 assets × ~15 fields, compressed integer codes)
   - **Total < 200 KB excluding D3 + fonts** (the brief said < 500 KB; we set a stretch target)
3. **D3 from CDN with SRI**: `<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js" integrity="sha384-..." crossorigin="anonymous"></script>`. Pin the version; never use `@latest`.
4. **First Contentful Paint < 1s on Fast 3G** (Lighthouse throttled). Achieved via: inline critical CSS (≤ 4KB) in `<head>`, defer D3 + app.js, preload fonts. Charts render on `DOMContentLoaded`; the hero text + skeleton paint immediately.
5. **No external API calls at runtime.** All data baked into `data.json` at build time (a tiny Python script in `scripts/build_demo_data.py` reads `classification/snapshot.csv` + `taxonomy.yaml` + a `decisions/` directory listing and emits one JSON). No CoinGecko, no GitHub API, no analytics, no telemetry. The site works fully offline once loaded.
6. **No cookies. No tracking.** Only `localStorage` for theme preference. Document this in the footer.
7. **Static GitHub Pages.** `gh-pages` branch built from `docs/` folder or via Actions workflow. No server-side anything.
8. **Browser support**: Last 2 versions of Chrome, Firefox, Safari, Edge. IE11 explicitly unsupported (D3 v7 dropped it). Mobile Safari iOS 15+.
9. **No emoji in production CSS or HTML.** This is a quant tool; pictograms are SVG icons (Lucide or hand-rolled), not Unicode emoji.
10. **Lighthouse targets** (each run on `npm run lighthouse` or equivalent CI):
    - Performance ≥ 95
    - Accessibility ≥ 95
    - Best Practices ≥ 95
    - SEO ≥ 90 (lower bar — single-page demo, not a content site)
11. **Determinism.** Given the same `data.json`, the same browser, the same window size, the rendered DOM is byte-identical. No `Math.random()` in chart layout, no current-date dependencies, no timezone-sensitive logic. The validation footer values are hard-coded from `validation.md` headline numbers, not computed at runtime.

---

## Appendix A — Asset list legend for the page hero

The hero displays:

```
crypto-sectors
An open hierarchical classification for digital assets.
158 assets · 4 classes · 14 sectors · ~35 sub-sectors · validated on 730 days of returns.
[ search input ]
[ View on GitHub ]   [ Read methodology ]
```

H1 in `--text-h1`, sub-line in `--text-lead --fg-1`, metadata line in `--text-small --fg-2 mono-mixed` (numbers in mono inline, labels in Inter). Two ghost buttons (border `--border`, transparent bg, hover `--bg-2`) at `--space-5` top margin.

## Appendix B — `data.json` schema (for engineer reference)

```json
{
  "version": "1.0.0",
  "generated_at": "2026-05-23",
  "classes": [
    {"code": 10, "name": "Digital Currencies", "color": "--class-10", "definition": "..."}
  ],
  "sectors": [
    {"code": 1010, "class_code": 10, "name": "Value Transfer Coins"}
  ],
  "sub_sectors": [
    {"code": 101010, "sector_code": 1010, "name": "Value Transfer Coins", "is_extension": false}
  ],
  "assets": [
    {"id": "btc", "symbol": "BTC", "name": "Bitcoin", "class": 10, "sector": 1010, "sub_sector": 101010, "chain": "BTC", "effective_from": "2024-05-23", "has_decision": false}
  ],
  "chain_order": ["BTC", "ETH", "SOL", "BNB", "TRX", "COSMOS", "AVAX", "NEAR", "MOVE", "OTHER"],
  "validation_headline": {
    "sector_spread": "+0.027",
    "sector_spread_ci": "[+0.021, +0.031]",
    "rolling_windows_positive": "19/19",
    "variance_explained_by_sector": "50.7%",
    "ic_sharpe_raw": "+0.742",
    "ic_sharpe_demeaned": "+0.642"
  }
}
```

`has_decision` is true iff `decisions/<id>.md` exists at build time. The asset card uses this to conditionally render the decisions link.

---

*End of DESIGN.md. If the implementation deviates from any value in this document, the deviation must be justified in a `decisions/` markdown file and this document updated in the same PR.*
