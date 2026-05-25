"""
build_site.py — Generate static HTML pages for the crypto-sectors site.

Rationale:
    The site should be self-contained: methodology, validation, per-asset deep
    pages, and decision rationales must all be accessible without jumping to
    GitHub raw view. This script renders all Markdown sources to HTML using
    Python's `markdown` library and writes static pages that GitHub Pages
    serves directly.

Inputs:
    methodology.md                      -> docs/methodology/index.html
    validation.md                       -> docs/validation/index.html
    validation/charts/*.png             -> docs/validation/charts/ (copied)
    decisions/*.md                      -> docs/decisions/<stem>/index.html
    classification/snapshot.csv         -> 158 asset rows
    data/descriptions.json              -> per-asset descriptions (optional)
    docs/_template.html                 -> shared site chrome template

Outputs:
    docs/methodology/index.html
    docs/validation/index.html
    docs/validation/charts/*.png        (binary copy)
    docs/decisions/<stem>/index.html
    docs/coins/<asset_id>/index.html    (158 pages)

Failure modes:
    - data/descriptions.json absent: proceeds with no descriptions (ok=false for all)
    - Missing validation/charts: validation page renders without broken image refs
    - Idempotent: running twice produces byte-identical output (no timestamps,
      deterministic ordering, no wall-clock strings in output files)

Usage:
    python scripts/build_site.py
"""

import csv
import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

try:
    import markdown
    from markdown.extensions.fenced_code import FencedCodeExtension
    from markdown.extensions.tables import TableExtension
    from markdown.extensions.toc import TocExtension
except ImportError:
    sys.exit("ERROR: 'markdown' package not installed. Run: pip install markdown")

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
TEMPLATE_FILE = DOCS_DIR / "_template.html"
SNAPSHOT_CSV = REPO_ROOT / "classification" / "snapshot.csv"
DATA_DIR = REPO_ROOT / "data"
DESCRIPTIONS_JSON = DATA_DIR / "descriptions.json"
VALIDATION_CHARTS_SRC = REPO_ROOT / "validation" / "charts"
TAXONOMY_JSON = DOCS_DIR / "data" / "taxonomy.json"

# Decision files that currently exist (stem -> title)
DECISION_FILES = list((REPO_ROOT / "decisions").glob("*.md"))

# Class code -> display name (mirrors taxonomy.json; hardcoded for zero runtime deps)
CLASS_NAMES = {
    "10": "Digital Currencies",
    "20": "Blockchain Infrastructure",
    "30": "Digital Asset Applications",
    "40": "Specialized Coins",
}
CLASS_COLORS = {
    "10": "var(--class-10)",
    "20": "var(--class-20)",
    "30": "var(--class-30)",
    "40": "var(--class-40)",
}
CLASS_COLORS_HEX = {
    "10": "hsl(36,78%,62%)",
    "20": "hsl(214,72%,64%)",
    "30": "hsl(286,56%,68%)",
    "40": "hsl(146,44%,56%)",
}

MD_EXTENSIONS = [
    FencedCodeExtension(),
    TableExtension(),
    TocExtension(permalink=True),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_template() -> str:
    """Load docs/_template.html. Fail fast if missing."""
    if not TEMPLATE_FILE.exists():
        sys.exit(f"ERROR: Template not found: {TEMPLATE_FILE}")
    return TEMPLATE_FILE.read_text(encoding="utf-8")


def render_md(text: str) -> str:
    """Render Markdown to HTML using python-markdown."""
    return markdown.markdown(text, extensions=MD_EXTENSIONS)


def rewrite_validation_image_links(html_text: str) -> str:
    """
    Convert image src paths like 'validation/charts/x.png' to 'charts/x.png'
    so they resolve relative to /validation/ where the page is served.
    """
    return re.sub(
        r'src="validation/charts/([^"]+)"',
        r'src="charts/\1"',
        html_text
    )


def fill_template(
    template: str,
    page_title: str,
    page_description: str,
    body_html: str,
    root_path: str = "../",
    footer_extra: str = "",
) -> str:
    """
    Fill the shared template with page-specific content.
    All substitution is positional (string.replace) — no external templating lib.
    """
    out = template
    out = out.replace("{{PAGE_TITLE}}", page_title)
    out = out.replace("{{PAGE_DESCRIPTION}}", page_description)
    out = out.replace("{{PAGE_BODY}}", body_html)
    out = out.replace("{{ROOT_PATH}}", root_path)
    out = out.replace("{{FOOTER_EXTRA}}", footer_extra)
    return out


def write_page(path: Path, content: str) -> None:
    """Write a page atomically; create parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def copy_binary(src: Path, dst: Path) -> None:
    """Copy binary file; create parent dirs."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def load_descriptions() -> dict:
    """Load data/descriptions.json. Returns empty dict if file absent."""
    if not DESCRIPTIONS_JSON.exists():
        print("  [warn] data/descriptions.json not found; descriptions will be empty")
        return {}
    with open(DESCRIPTIONS_JSON, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("assets", {})


def load_taxonomy_labels() -> dict:
    """
    Load sector and sub-sector labels from docs/data/taxonomy.json.
    Returns {code_str: name_str} for sectors and sub-sectors.
    Falls back to empty if file absent.
    """
    labels = {}
    if not TAXONOMY_JSON.exists():
        return labels
    with open(TAXONOMY_JSON, encoding="utf-8") as f:
        tax = json.load(f)
    # assets_flat has all the codes and names we need
    for a in tax.get("assets_flat", []):
        labels[str(a.get("sector_code", ""))] = a.get("sector_name", "")
        labels[str(a.get("sub_sector_code", ""))] = a.get("sub_sector_name", "")
        labels[str(a.get("class_code", ""))] = a.get("class_name", "")
    return labels


def read_snapshot() -> list[dict]:
    """Read classification/snapshot.csv and return list of row dicts."""
    rows = []
    with open(SNAPSHOT_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# Page builders
# ---------------------------------------------------------------------------

def build_methodology_page(template: str) -> None:
    """Render methodology.md to docs/methodology/index.html."""
    src = REPO_ROOT / "methodology.md"
    if not src.exists():
        print("  [skip] methodology.md not found")
        return

    md_text = src.read_text(encoding="utf-8")
    body_html = render_md(md_text)

    page_body = f"""
<div class="container prose-page">
<article class="prose">
{body_html}
</article>
</div>
"""

    content = fill_template(
        template=template,
        page_title="Methodology",
        page_description=(
            "Full methodology for the crypto-sectors open industry classification. "
            "Covers hierarchy design, classification criteria, validation approach, "
            "and decision audit trail."
        ),
        body_html=page_body,
        root_path="../",
    )

    out = DOCS_DIR / "methodology" / "index.html"
    write_page(out, content)
    print(f"  -> {out} ({len(content)} chars)")


def build_validation_page(template: str) -> None:
    """Render validation.md to docs/validation/index.html and copy charts."""
    src = REPO_ROOT / "validation.md"
    if not src.exists():
        print("  [skip] validation.md not found")
        return

    md_text = src.read_text(encoding="utf-8")
    body_html = render_md(md_text)
    body_html = rewrite_validation_image_links(body_html)

    # Copy validation/charts/ -> docs/validation/charts/
    if VALIDATION_CHARTS_SRC.exists():
        dst_charts = DOCS_DIR / "validation" / "charts"
        for png in sorted(VALIDATION_CHARTS_SRC.glob("*.png")):
            copy_binary(png, dst_charts / png.name)
            print(f"  [copy] {png.name} -> docs/validation/charts/")

    page_body = f"""
<div class="container prose-page">
<article class="prose">
{body_html}
</article>
</div>
"""

    content = fill_template(
        template=template,
        page_title="Validation",
        page_description=(
            "Empirical validation report for the crypto-sectors classification. "
            "Covers within-vs-between sector spread, rolling stability, and "
            "baseline comparisons over 730 days of daily returns."
        ),
        body_html=page_body,
        root_path="../",
    )

    out = DOCS_DIR / "validation" / "index.html"
    write_page(out, content)
    print(f"  -> {out} ({len(content)} chars)")


def build_decision_pages(template: str) -> None:
    """Render decisions/*.md to docs/decisions/<stem>/index.html."""
    decisions_dir = REPO_ROOT / "decisions"
    if not decisions_dir.exists():
        return

    for md_file in sorted(decisions_dir.glob("*.md")):
        if md_file.stem == "README":
            continue
        stem = md_file.stem
        md_text = md_file.read_text(encoding="utf-8")

        # Extract title from first H1
        first_line = md_text.split("\n", 1)[0].strip()
        title = first_line.lstrip("#").strip() if first_line.startswith("#") else stem

        body_html = render_md(md_text)

        page_body = f"""
<div class="container prose-page">
<p class="prose-breadcrumb">
<a href="../../" class="accent-link">crypto-sectors</a>
 &rsaquo; Decisions
</p>
<article class="prose">
{body_html}
</article>
<p class="prose-source-link">
<a href="https://github.com/quantbai/crypto-sectors/blob/main/decisions/{md_file.name}"
   class="accent-link" target="_blank" rel="noopener noreferrer">
View source on GitHub
</a>
</p>
</div>
"""

        content = fill_template(
            template=template,
            page_title=f"Decision: {title}",
            page_description=f"Classification decision rationale for {title}.",
            body_html=page_body,
            root_path="../../",
        )

        out = DOCS_DIR / "decisions" / stem / "index.html"
        write_page(out, content)
        print(f"  -> {out}")


def build_coin_pages(template: str, rows: list[dict], descriptions: dict, labels: dict) -> int:
    """
    Build one page per asset. Returns count of pages written.
    docs/coins/<asset_id>/index.html
    """
    # Build set of known decision files for quick lookup
    decision_stems = {f.stem for f in (REPO_ROOT / "decisions").glob("*.md")
                      if f.stem != "README"}

    written = 0
    for row in rows:
        aid = row["asset_id"]
        symbol = row["symbol"]
        name = row["name"]
        class_code = row["class_code"]
        sector_code = row["sector_code"]
        sub_sector_code = row["sub_sector_code"]
        chain = row["chain_ecosystem"]
        effective_from = row["effective_from"]

        # Labels from taxonomy
        class_name = CLASS_NAMES.get(class_code, class_code)
        sector_name = labels.get(sector_code, sector_code)
        sub_sector_name = labels.get(sub_sector_code, sub_sector_code)
        class_color_hex = CLASS_COLORS_HEX.get(class_code, "#888")

        # Description
        desc_entry = descriptions.get(aid, {})
        short_desc = desc_entry.get("short_desc")
        long_desc = desc_entry.get("long_desc_html_safe")
        cg_id = desc_entry.get("cg_id", aid)
        desc_ok = desc_entry.get("ok", False)

        # Decision doc
        has_decision = aid in decision_stems
        decision_slug = aid  # stem matches asset_id in all current cases

        # Build classification chips
        chips_html = f"""
<div class="coin-chips">
<span class="code-chip" style="color:{class_color_hex};">{class_code} {class_name}</span>
<span class="code-chip">{sector_code} {sector_name}</span>
<span class="code-chip">{sub_sector_code} {sub_sector_name}</span>
</div>
"""

        # About section
        if short_desc:
            about_section = f"""
<section class="coin-section">
<h2>About</h2>
<p>{short_desc}</p>
{f'<p class="text-small" style="color:var(--fg-2);">{long_desc}</p>' if long_desc and long_desc != short_desc else ""}
</section>
"""
        else:
            about_section = ""

        # Classification table
        classification_table = f"""
<section class="coin-section">
<h2>Classification</h2>
<table class="coin-table">
<thead><tr><th>Field</th><th>Value</th></tr></thead>
<tbody>
<tr><td>Class</td><td><span class="code-chip" style="color:{class_color_hex};">{class_code}</span> {class_name}</td></tr>
<tr><td>Sector</td><td><span class="code-chip">{sector_code}</span> {sector_name}</td></tr>
<tr><td>Sub-sector</td><td><span class="code-chip">{sub_sector_code}</span> {sub_sector_name}</td></tr>
<tr><td>Chain ecosystem</td><td>{chain}</td></tr>
<tr><td>Effective from</td><td><code>{effective_from}</code></td></tr>
<tr><td>Asset ID</td><td><code>{aid}</code></td></tr>
</tbody>
</table>
</section>
"""

        # Decision rationale section (only if decision file exists)
        if has_decision:
            decision_content = (REPO_ROOT / "decisions" / f"{decision_slug}.md").read_text(encoding="utf-8")
            decision_html = render_md(decision_content)
            decision_section = f"""
<section class="coin-section">
<h2>Decision rationale</h2>
<div class="prose">
{decision_html}
</div>
</section>
"""
        else:
            decision_section = ""

        # Source links
        links = []
        if cg_id:
            links.append(
                f'<a href="https://www.coingecko.com/en/coins/{cg_id}" '
                f'class="accent-link" target="_blank" rel="noopener noreferrer">CoinGecko</a>'
            )
        if has_decision:
            links.append(
                f'<a href="https://github.com/quantbai/crypto-sectors/blob/main/decisions/{decision_slug}.md" '
                f'class="accent-link" target="_blank" rel="noopener noreferrer">Decision on GitHub</a>'
            )
        source_links_html = " &middot; ".join(links) if links else ""
        source_section = f"""
<section class="coin-section coin-section--links">
<h2>Source links</h2>
<p>{source_links_html}</p>
</section>
""" if links else ""

        # CoinGecko attribution footer extra
        footer_extra = ""
        if desc_ok:
            footer_extra = '<p class="footer-text">Description &copy; <a href="https://www.coingecko.com" class="footer-link" target="_blank" rel="noopener noreferrer">CoinGecko</a> (CC BY 4.0)</p>'

        page_body = f"""
<div class="container prose-page">
<p class="prose-breadcrumb">
<a href="../../" class="accent-link">crypto-sectors</a>
 &rsaquo; Coins
</p>
<div class="coin-header">
<div class="coin-class-stripe" style="background:{class_color_hex};"></div>
<div class="coin-header-inner">
<h1><span class="mono">{symbol}</span> &mdash; {name}</h1>
{chips_html}
</div>
</div>
{about_section}
{classification_table}
{decision_section}
{source_section}
</div>
"""

        content = fill_template(
            template=template,
            page_title=f"{symbol} — {name}",
            page_description=f"{symbol} ({name}) classification: {class_name}, {sector_name}, {sub_sector_name}. {short_desc or ''}",
            body_html=page_body,
            root_path="../../",
            footer_extra=footer_extra,
        )

        out = DOCS_DIR / "coins" / aid / "index.html"
        write_page(out, content)
        written += 1

    print(f"  -> docs/coins/: {written} pages written")
    return written


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """
    Build all static site pages. Idempotent: rerunning produces identical output.
    """
    print("[build_site] Starting site build")

    template = load_template()
    descriptions = load_descriptions()
    labels = load_taxonomy_labels()
    rows = read_snapshot()

    ok_desc = sum(1 for aid in [r["asset_id"] for r in rows]
                  if descriptions.get(aid, {}).get("ok", False))
    print(f"  Descriptions: {ok_desc}/{len(rows)} assets have descriptions")

    print("[build_site] Building methodology page")
    build_methodology_page(template)

    print("[build_site] Building validation page")
    build_validation_page(template)

    print("[build_site] Building decision pages")
    build_decision_pages(template)

    print("[build_site] Building coin pages (158 assets)")
    n = build_coin_pages(template, rows, descriptions, labels)

    print(f"[build_site] Done. {n} coin pages, methodology, validation, decisions built.")


if __name__ == "__main__":
    main()
