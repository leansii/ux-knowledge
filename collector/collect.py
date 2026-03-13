#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "requests>=2.28",
#     "beautifulsoup4>=4.12",
#     "pyyaml>=6.0",
# ]
# ///
"""
UX Patterns Collector
Scrapes pattern data from ui-patterns.com and outputs structured YAML files.

Usage:
    uv run collect.py                          # Collect all patterns
    uv run collect.py --pattern drag-and-drop  # Collect single pattern
    uv run collect.py --dry-run                # List URLs without fetching
    uv run collect.py --output ../patterns     # Custom output directory
"""

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

try:
    import requests
    from bs4 import BeautifulSoup, Tag
    import yaml
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install -r requirements.txt")
    sys.exit(1)


BASE_URL = "https://ui-patterns.com"
INDEX_URL = f"{BASE_URL}/patterns"
REQUEST_DELAY = 1.5  # seconds between requests (be polite)
USER_AGENT = "UXKnowledge-Collector/1.0 (educational; github.com/leansii/ux-knowledge)"


@dataclass
class PatternData:
    id: str
    name: str
    url: str
    category: str = ""
    subcategory: str = ""
    group: str = ""  # "ui" or "persuasive"
    problem: str = ""
    usage: list = field(default_factory=list)
    solution: str = ""
    rationale: str = ""
    discussion: str = ""
    example_sites: list = field(default_factory=list)
    votes_up: int = 0
    votes_down: int = 0


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    })
    return session


def fetch_page(session: requests.Session, url: str) -> Optional[BeautifulSoup]:
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as e:
        print(f"  ERROR fetching {url}: {e}", file=sys.stderr)
        return None


def parse_index(soup: BeautifulSoup) -> list[dict]:
    """Parse the index page to extract all pattern URLs with their categories."""
    patterns = []
    seen_ids = set()

    # Find the two main sections
    sections = [
        ("ui", "User Interface Design Patterns"),
        ("persuasive", "Persuasive Design Patterns"),
    ]

    for group, section_title in sections:
        # Find the h2 for this section
        h2 = soup.find("h2", string=re.compile(re.escape(section_title), re.I))
        if not h2:
            print(f"  WARNING: Could not find section '{section_title}'", file=sys.stderr)
            continue

        # Structure: h2 is inside div.col > div.row
        # The category content is in the NEXT div.row sibling
        row_div = h2.parent.parent  # div.row containing the h2
        container = row_div.find_next_sibling("div")
        if not container:
            continue

        # Each top-level div is a category (wrapped in col > row)
        category_divs = container.find_all("div", recursive=False)
        if not category_divs:
            # Try one level deeper (col-xs-12 wrapper)
            inner = container.find("div")
            if inner:
                category_divs = inner.find_all("div", recursive=False)
        for cat_div in category_divs:
            # Category name from the first link (may be nested inside inner div)
            cat_link = cat_div.find("a", href=re.compile(r"/patterns/.+/list"))
            category = cat_link.get_text(strip=True) if cat_link else "Unknown"

            # Subcategories are in <li> with <strong>
            for li in cat_div.find_all("li", recursive=True):
                strong = li.find("strong", recursive=False)
                if not strong:
                    continue
                subcategory = strong.get_text(strip=True)

                # Pattern links are in the nested <ul>
                sub_list = li.find("ul")
                if not sub_list:
                    continue

                for pattern_li in sub_list.find_all("li", recursive=False):
                    link = pattern_li.find("a")
                    if not link or not link.get("href", "").startswith("/patterns/"):
                        continue

                    href = link["href"]
                    pattern_id = href.split("/patterns/")[-1]

                    if pattern_id in seen_ids:
                        continue
                    seen_ids.add(pattern_id)

                    display_name = link.get_text(strip=True)

                    patterns.append({
                        "id": pattern_id,
                        "name": display_name,
                        "url": f"{BASE_URL}{href}",
                        "category": category,
                        "subcategory": subcategory,
                        "group": group,
                    })

    return patterns


def clean_text(text: str) -> str:
    """Clean extracted text: normalize whitespace, strip."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_pattern_page(soup: BeautifulSoup, meta: dict) -> PatternData:
    """Parse a single pattern page and extract all sections."""
    pattern = PatternData(
        id=meta["id"],
        name=meta["name"],
        url=meta["url"],
        category=meta["category"],
        subcategory=meta["subcategory"],
        group=meta["group"],
    )

    # Find the main content area
    main = soup.find("main") or soup

    def collect_section_text(h2_elem) -> str:
        """Collect text from siblings after an h2 until the next h2."""
        parts = []
        sibling = h2_elem.next_sibling
        while sibling:
            if isinstance(sibling, Tag):
                if sibling.name == "h2":
                    break
                # Stop at toolbar/social sharing divs
                if sibling.name == "div" and sibling.find("a", href=re.compile("facebook|twitter|ratings")):
                    break
                # Stop at nav sections (pattern index at bottom)
                if sibling.name in ("nav",) or (sibling.name == "div" and sibling.find("h2")):
                    break
                text = clean_text(sibling.get_text())
                if text:
                    parts.append(text)
            sibling = sibling.next_sibling
        return "\n".join(parts)

    # Skip headings that are part of the bottom navigation index
    skip_titles = {"user interface design patterns", "persuasive design patterns"}

    # Extract sections by h2 headings
    headings = main.find_all("h2")
    for h2 in headings:
        title = h2.get_text(strip=True).lower()

        if title in skip_titles:
            continue

        if "problem" in title:
            pattern.problem = collect_section_text(h2)

        elif title == "usage":
            # Look for a <ul> as next sibling
            ul = h2.find_next_sibling("ul")
            if not ul:
                # Try inside a wrapper div
                next_sib = h2.find_next_sibling()
                if next_sib and next_sib.name == "div":
                    ul = next_sib.find("ul")
            if ul:
                pattern.usage = [
                    clean_text(li.get_text())
                    for li in ul.find_all("li", recursive=False)
                    if clean_text(li.get_text())
                ]

        elif title == "solution":
            pattern.solution = collect_section_text(h2)

        elif title == "rationale":
            pattern.rationale = collect_section_text(h2)

        elif title == "discussion":
            pattern.discussion = collect_section_text(h2)

        elif title == "example":
            next_sib = h2.find_next_sibling()
            if next_sib:
                for link in next_sib.find_all("a"):
                    site_name = link.get_text(strip=True)
                    if site_name and not site_name.startswith("http"):
                        pattern.example_sites.append(site_name)

    # Extract votes
    vote_links = main.find_all("a", href=re.compile(r"/ratings\?"))
    for link in vote_links:
        text = link.get_text(strip=True)
        if not text:
            continue
        try:
            num = int(re.sub(r"[^\d]", "", text))
            if "up" in link.get("href", ""):
                pattern.votes_up = num
            elif "down" in link.get("href", ""):
                pattern.votes_down = num
        except (ValueError, AttributeError):
            pass

    return pattern


def to_yaml_friendly(pattern: PatternData) -> dict:
    """Convert PatternData to a clean dict for YAML output."""
    d = {
        "id": pattern.id,
        "name": pattern.name,
        "url": pattern.url,
        "group": pattern.group,
        "category": pattern.category,
        "subcategory": pattern.subcategory,
    }
    if pattern.problem:
        d["problem"] = pattern.problem
    if pattern.usage:
        d["usage"] = pattern.usage
    if pattern.solution:
        d["solution"] = pattern.solution
    if pattern.rationale:
        d["rationale"] = pattern.rationale
    if pattern.discussion:
        d["discussion"] = pattern.discussion
    if pattern.example_sites:
        d["example_sites"] = pattern.example_sites
    d["votes"] = {"up": pattern.votes_up, "down": pattern.votes_down}
    return d


def represent_str(dumper, data):
    """Use block scalar style for multiline strings in YAML."""
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    if len(data) > 120:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=">")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def save_results(patterns: list[dict], output_dir: Path):
    """Save collected patterns to YAML and JSON files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Custom YAML dumper for readable output
    yaml.add_representer(str, represent_str)

    # Full collected data
    yaml_path = output_dir / "collected-patterns.yaml"
    with open(yaml_path, "w") as f:
        f.write("# Collected from ui-patterns.com\n")
        f.write(f"# {len(patterns)} patterns\n\n")
        yaml.dump(patterns, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=100)
    print(f"  Saved YAML: {yaml_path}")

    # JSON for programmatic use
    json_path = output_dir / "collected-patterns.json"
    with open(json_path, "w") as f:
        json.dump(patterns, f, indent=2, ensure_ascii=False)
    print(f"  Saved JSON: {json_path}")

    # Summary stats
    groups = {}
    for p in patterns:
        g = p.get("group", "unknown")
        groups[g] = groups.get(g, 0) + 1
    print(f"\n  Total: {len(patterns)} patterns")
    for g, count in sorted(groups.items()):
        print(f"    {g}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Collect UX patterns from ui-patterns.com")
    parser.add_argument("--output", "-o", default=None,
                        help="Output directory (default: ./output)")
    parser.add_argument("--pattern", "-p", default=None,
                        help="Collect a single pattern by ID (e.g., drag-and-drop)")
    parser.add_argument("--dry-run", action="store_true",
                        help="List pattern URLs without fetching individual pages")
    parser.add_argument("--delay", type=float, default=REQUEST_DELAY,
                        help=f"Delay between requests in seconds (default: {REQUEST_DELAY})")
    parser.add_argument("--resume-from", default=None,
                        help="Resume collection from this pattern ID (skip earlier ones)")
    parser.add_argument("--save-every", type=int, default=10,
                        help="Save intermediate results every N patterns (default: 10)")
    args = parser.parse_args()

    output_dir = Path(args.output) if args.output else Path(__file__).parent / "output"
    session = get_session()

    # Step 1: Fetch and parse the index page
    print(f"Fetching index: {INDEX_URL}")
    index_soup = fetch_page(session, INDEX_URL)
    if not index_soup:
        print("Failed to fetch index page", file=sys.stderr)
        sys.exit(1)

    all_patterns = parse_index(index_soup)
    print(f"Found {len(all_patterns)} patterns on index page")

    if args.dry_run:
        for p in all_patterns:
            print(f"  [{p['group']}] {p['category']} > {p['subcategory']} > {p['name']}")
            print(f"    {p['url']}")
        return

    # Filter to single pattern if requested
    if args.pattern:
        all_patterns = [p for p in all_patterns if p["id"] == args.pattern]
        if not all_patterns:
            print(f"Pattern '{args.pattern}' not found in index", file=sys.stderr)
            sys.exit(1)

    # Resume support
    if args.resume_from:
        skip = True
        filtered = []
        for p in all_patterns:
            if p["id"] == args.resume_from:
                skip = False
            if not skip:
                filtered.append(p)
        if skip:
            print(f"Resume pattern '{args.resume_from}' not found", file=sys.stderr)
            sys.exit(1)
        print(f"Resuming from '{args.resume_from}', {len(filtered)} patterns remaining")
        all_patterns = filtered

    # Load existing results for resume
    existing_results = []
    json_path = output_dir / "collected-patterns.json"
    if json_path.exists() and args.resume_from:
        with open(json_path) as f:
            existing_results = json.load(f)
        print(f"Loaded {len(existing_results)} previously collected patterns")

    # Step 2: Fetch each pattern page
    results = list(existing_results)
    collected_ids = {r["id"] for r in results}
    total = len(all_patterns)

    for i, meta in enumerate(all_patterns, 1):
        if meta["id"] in collected_ids:
            print(f"  [{i}/{total}] {meta['name']} — already collected, skipping")
            continue

        print(f"  [{i}/{total}] {meta['name']} ({meta['url']})")

        soup = fetch_page(session, meta["url"])
        if not soup:
            print(f"    SKIPPED (fetch failed)")
            continue

        pattern = parse_pattern_page(soup, meta)
        result = to_yaml_friendly(pattern)
        results.append(result)

        # Show what we got
        sections = []
        if pattern.problem:
            sections.append("problem")
        if pattern.usage:
            sections.append(f"usage({len(pattern.usage)})")
        if pattern.solution:
            sections.append("solution")
        if pattern.rationale:
            sections.append("rationale")
        if pattern.discussion:
            sections.append("discussion")
        print(f"    Extracted: {', '.join(sections) or 'no content found'}")

        # Intermediate save
        if args.save_every and i % args.save_every == 0:
            print(f"  --- Saving intermediate results ({len(results)} patterns) ---")
            save_results(results, output_dir)

        # Be polite
        if i < total:
            time.sleep(args.delay)

    # Step 3: Save final results
    print(f"\nSaving final results...")
    save_results(results, output_dir)
    print("Done!")


if __name__ == "__main__":
    main()
