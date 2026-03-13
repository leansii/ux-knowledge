#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
"""
Compare collected (scraped) patterns with curated patterns.

Usage:
    uv run compare.py
    uv run compare.py --verbose
    uv run compare.py --output report.md
"""

import argparse
import json
import sys
from pathlib import Path
from difflib import SequenceMatcher

import yaml


def similarity(a: str, b: str) -> float:
    """Return 0-1 similarity ratio between two strings."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def load_collected(path: Path) -> dict:
    """Load collected patterns, keyed by ID."""
    with open(path) as f:
        data = json.load(f)
    return {p["id"]: p for p in data}


def load_curated(path: Path) -> dict:
    """Load curated patterns YAML, keyed by ID."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return {p["id"]: p for p in data}


def compare_field(curated_val, collected_val, field_name: str) -> dict:
    """Compare a single field between curated and collected."""
    if isinstance(curated_val, list):
        curated_text = " | ".join(str(v) for v in curated_val)
    else:
        curated_text = str(curated_val or "")

    if isinstance(collected_val, list):
        collected_text = " | ".join(str(v) for v in collected_val)
    else:
        collected_text = str(collected_val or "")

    sim = similarity(curated_text, collected_text)

    return {
        "field": field_name,
        "similarity": sim,
        "curated_empty": not curated_text.strip(),
        "collected_empty": not collected_text.strip(),
        "curated_len": len(curated_text),
        "collected_len": len(collected_text),
        "curated": curated_text[:200],
        "collected": collected_text[:200],
    }


def main():
    parser = argparse.ArgumentParser(description="Compare collected vs curated patterns")
    parser.add_argument("--collected", default=None, help="Path to collected JSON")
    parser.add_argument("--curated", default=None, help="Path to curated YAML")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--output", "-o", default=None, help="Save report to file")
    args = parser.parse_args()

    base = Path(__file__).parent.parent
    collected_path = Path(args.collected) if args.collected else Path(__file__).parent / "output" / "collected-patterns.json"
    curated_path = Path(args.curated) if args.curated else base / "patterns" / "ux-patterns.yaml"

    if not collected_path.exists():
        print(f"Collected data not found: {collected_path}")
        print("Run 'uv run collect.py' first")
        sys.exit(1)

    collected = load_collected(collected_path)
    curated = load_curated(curated_path)

    lines = []
    def out(s=""):
        lines.append(s)
        if not args.output:
            print(s)

    # Summary
    out("# Curated vs Collected Comparison")
    out()
    out(f"- Curated patterns: {len(curated)}")
    out(f"- Collected patterns: {len(collected)}")

    curated_ids = set(curated.keys())
    collected_ids = set(collected.keys())

    only_curated = curated_ids - collected_ids
    only_collected = collected_ids - curated_ids
    common = curated_ids & collected_ids

    out(f"- In both: {len(common)}")
    if only_curated:
        out(f"- Only in curated: {len(only_curated)} — {sorted(only_curated)}")
    if only_collected:
        out(f"- Only in collected: {len(only_collected)} — {sorted(only_collected)}")
    out()

    # Field-by-field comparison
    fields_to_compare = [
        ("problem", "problem"),
        ("solution", "solution"),
    ]

    # Aggregate stats
    field_stats = {}
    pattern_details = []

    for pid in sorted(common):
        c = curated[pid]
        s = collected[pid]

        detail = {"id": pid, "name": c.get("name", pid), "fields": []}

        for curated_field, collected_field in fields_to_compare:
            curated_val = c.get(curated_field, "")
            collected_val = s.get(collected_field, "")
            result = compare_field(curated_val, collected_val, curated_field)
            detail["fields"].append(result)

            if curated_field not in field_stats:
                field_stats[curated_field] = []
            field_stats[curated_field].append(result["similarity"])

        # Compare usage (curated: when_to_use) vs (collected: usage)
        curated_usage = c.get("when_to_use", [])
        collected_usage = s.get("usage", [])
        result = compare_field(curated_usage, collected_usage, "when_to_use/usage")
        detail["fields"].append(result)
        if "when_to_use" not in field_stats:
            field_stats["when_to_use"] = []
        field_stats["when_to_use"].append(result["similarity"])

        # Check collected fields that curated doesn't have
        has_rationale = bool(s.get("rationale", "").strip())
        has_discussion = bool(s.get("discussion", "").strip())
        detail["extra_collected"] = {
            "rationale": has_rationale,
            "discussion": has_discussion,
        }

        pattern_details.append(detail)

    # Field similarity summary
    out("## Field Similarity (average)")
    out()
    out("| Field | Avg Similarity | Min | Max | Curated empty | Collected empty |")
    out("|-------|---------------|-----|-----|---------------|-----------------|")
    for field_name, sims in field_stats.items():
        avg = sum(sims) / len(sims) if sims else 0
        mn = min(sims) if sims else 0
        mx = max(sims) if sims else 0
        # Count empties
        details_for_field = [d for p in pattern_details for d in p["fields"] if d["field"] == field_name or (field_name == "when_to_use" and d["field"] == "when_to_use/usage")]
        c_empty = sum(1 for d in details_for_field if d["curated_empty"])
        s_empty = sum(1 for d in details_for_field if d["collected_empty"])
        out(f"| {field_name} | {avg:.1%} | {mn:.1%} | {mx:.1%} | {c_empty} | {s_empty} |")
    out()

    # Extra fields only in collected
    has_rationale = sum(1 for d in pattern_details if d["extra_collected"]["rationale"])
    has_discussion = sum(1 for d in pattern_details if d["extra_collected"]["discussion"])
    out("## Extra fields in collected data (not in curated)")
    out()
    out(f"- Patterns with **rationale**: {has_rationale}/{len(common)}")
    out(f"- Patterns with **discussion**: {has_discussion}/{len(common)}")
    out()

    # Distribution of similarity
    out("## Problem similarity distribution")
    out()
    problem_sims = field_stats.get("problem", [])
    buckets = {"0-20%": 0, "20-40%": 0, "40-60%": 0, "60-80%": 0, "80-100%": 0}
    for s in problem_sims:
        if s < 0.2: buckets["0-20%"] += 1
        elif s < 0.4: buckets["20-40%"] += 1
        elif s < 0.6: buckets["40-60%"] += 1
        elif s < 0.8: buckets["60-80%"] += 1
        else: buckets["80-100%"] += 1
    for bucket, count in buckets.items():
        bar = "#" * count
        out(f"  {bucket:>8s}: {count:3d} {bar}")
    out()

    # Lowest similarity patterns (most different from source)
    out("## Most different patterns (lowest problem similarity)")
    out()
    sorted_by_sim = sorted(pattern_details, key=lambda d: next(f["similarity"] for f in d["fields"] if f["field"] == "problem"))
    for d in sorted_by_sim[:15]:
        prob = next(f for f in d["fields"] if f["field"] == "problem")
        out(f"### {d['name']} ({d['id']}) — {prob['similarity']:.0%}")
        out(f"  Curated:   {prob['curated']}")
        out(f"  Collected: {prob['collected']}")
        out()

    # Highest similarity patterns
    if args.verbose:
        out("## Most similar patterns (highest problem similarity)")
        out()
        for d in sorted_by_sim[-10:]:
            prob = next(f for f in d["fields"] if f["field"] == "problem")
            out(f"### {d['name']} ({d['id']}) — {prob['similarity']:.0%}")
            out(f"  Curated:   {prob['curated']}")
            out(f"  Collected: {prob['collected']}")
            out()

    # Save report
    if args.output:
        with open(args.output, "w") as f:
            f.write("\n".join(lines))
        print(f"Report saved to {args.output}")


if __name__ == "__main__":
    main()
