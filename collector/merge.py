#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
"""
Merge curated and collected pattern data into enriched YAML files.

Strategy:
  - Keep curated structure as base (when_to_use, avoid_when, related_patterns, tags, solution)
  - Add from collected: rationale, discussion, source_problem, usage, votes
  - Problem: keep curated (concise), add original as source_problem
  - Solution: keep curated (detailed), add rationale as separate field

Usage:
    uv run merge.py
    uv run merge.py --dry-run
"""

import argparse
import json
import sys
from pathlib import Path

import yaml


def represent_str(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    if len(data) > 120:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=">")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def represent_list(dumper, data):
    """Use flow style for short lists (tags, related_patterns)."""
    if all(isinstance(item, str) and len(item) < 30 for item in data):
        total = sum(len(str(item)) for item in data)
        if total < 100:
            return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=False)


def load_collected(path: Path) -> dict:
    with open(path) as f:
        data = json.load(f)
    return {p["id"]: p for p in data}


def load_curated(path: Path) -> dict:
    with open(path) as f:
        data = yaml.safe_load(f)
    return {p["id"]: p for p in data}


def merge_pattern(curated: dict, collected: dict) -> dict:
    """Merge a single pattern from both sources."""
    merged = {}

    # Identity
    merged["id"] = curated["id"]
    merged["name"] = curated["name"]

    # Problem: keep curated (concise, action-oriented)
    merged["problem"] = curated.get("problem", "")

    # Source problem: add original if meaningfully different
    source_problem = collected.get("problem", "").strip()
    if source_problem and source_problem != merged["problem"]:
        merged["source_problem"] = source_problem

    # When to use: keep curated
    if curated.get("when_to_use"):
        merged["when_to_use"] = curated["when_to_use"]

    # Solution: keep curated (detailed implementation guidance)
    if curated.get("solution"):
        merged["solution"] = curated["solution"]

    # Rationale: NEW from collected (why it works psychologically)
    rationale = collected.get("rationale", "").strip()
    if rationale:
        merged["rationale"] = rationale

    # Discussion: NEW from collected (caveats, nuances)
    discussion = collected.get("discussion", "").strip()
    if discussion:
        merged["discussion"] = discussion

    # Avoid when: keep curated
    if curated.get("avoid_when"):
        merged["avoid_when"] = curated["avoid_when"]

    # Related patterns: keep curated
    if curated.get("related_patterns"):
        merged["related_patterns"] = curated["related_patterns"]

    # Tags: keep curated
    if curated.get("tags"):
        merged["tags"] = curated["tags"]

    # Source metadata
    source_url = collected.get("url", "")
    if source_url:
        merged["source_url"] = source_url

    votes = collected.get("votes", {})
    if votes.get("up", 0) > 0 or votes.get("down", 0) > 0:
        merged["votes"] = votes

    return merged


def build_index(patterns: list) -> list:
    """Build compact index from merged patterns."""
    index = []
    for p in patterns:
        entry = {
            "id": p["id"],
            "p": p.get("problem", ""),
            "t": p.get("tags", []),
        }
        index.append(entry)
    return index


def main():
    parser = argparse.ArgumentParser(description="Merge curated + collected into enriched patterns")
    parser.add_argument("--dry-run", action="store_true", help="Show stats without writing files")
    parser.add_argument("--output", "-o", default=None, help="Output directory")
    args = parser.parse_args()

    base = Path(__file__).parent.parent
    collected_path = Path(__file__).parent / "output" / "collected-patterns.json"
    curated_path = base / "patterns" / "ux-patterns.yaml"
    output_dir = Path(args.output) if args.output else base / "patterns"

    if not collected_path.exists():
        print("Collected data not found. Run 'uv run collect.py' first.")
        sys.exit(1)

    collected = load_collected(collected_path)
    curated = load_curated(curated_path)

    print(f"Curated: {len(curated)} patterns")
    print(f"Collected: {len(collected)} patterns")

    # Merge
    merged = []
    stats = {"rationale_added": 0, "discussion_added": 0, "source_problem_added": 0, "total": 0}

    for pid, c in curated.items():
        s = collected.get(pid, {})
        m = merge_pattern(c, s)
        merged.append(m)
        stats["total"] += 1
        if "rationale" in m:
            stats["rationale_added"] += 1
        if "discussion" in m:
            stats["discussion_added"] += 1
        if "source_problem" in m:
            stats["source_problem_added"] += 1

    print(f"\nMerge results:")
    print(f"  Total patterns: {stats['total']}")
    print(f"  + rationale: {stats['rationale_added']}")
    print(f"  + discussion: {stats['discussion_added']}")
    print(f"  + source_problem: {stats['source_problem_added']}")

    if args.dry_run:
        print("\nDry run — no files written.")
        # Show a sample
        sample = merged[0]
        print(f"\nSample ({sample['id']}):")
        yaml.add_representer(str, represent_str)
        yaml.add_representer(list, represent_list)
        print(yaml.dump([sample], default_flow_style=False, allow_unicode=True, sort_keys=False, width=100))
        return

    # Write enriched patterns
    yaml.add_representer(str, represent_str)
    yaml.add_representer(list, represent_list)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Full reference
    full_path = output_dir / "ux-patterns.yaml"
    with open(full_path, "w") as f:
        f.write("# UX Patterns Full Reference — enriched with source data\n")
        f.write(f"# {len(merged)} patterns\n")
        f.write("# Fields: problem, source_problem, when_to_use, solution, rationale, discussion,\n")
        f.write("#         avoid_when, related_patterns, tags, source_url, votes\n\n")
        yaml.dump(merged, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=100)
    print(f"\nSaved: {full_path}")

    # Compact index (unchanged structure, same problem text)
    index = build_index(merged)
    index_path = output_dir / "ux-patterns-index.yaml"
    with open(index_path, "w") as f:
        f.write("# UX Patterns Index — 170 patterns\n")
        f.write("# Format: id, p (problem), t (tags)\n\n")
        yaml.dump(index, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=100)
    print(f"Saved: {index_path}")

    # Stats
    full_lines = full_path.read_text().count("\n")
    index_lines = index_path.read_text().count("\n")
    print(f"\nFull reference: {full_lines} lines")
    print(f"Index: {index_lines} lines")


if __name__ == "__main__":
    main()
