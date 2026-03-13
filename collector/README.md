# UX Patterns Collector

Scrapes pattern data from [ui-patterns.com](https://ui-patterns.com/patterns) into structured YAML/JSON.

## Usage

Uses [uv](https://docs.astral.sh/uv/) — dependencies are declared inline in the script, no setup needed.

```bash
cd collector

# Collect all 170 patterns (~5 minutes with default delay)
uv run collect.py

# Preview what will be collected without fetching
uv run collect.py --dry-run

# Collect a single pattern
uv run collect.py --pattern drag-and-drop

# Resume interrupted collection
uv run collect.py --resume-from Wizard

# Custom output directory and delay
uv run collect.py --output ../patterns/raw --delay 2.0
```

## Output

Results are saved to `collector/output/`:
- `collected-patterns.yaml` — human-readable YAML
- `collected-patterns.json` — machine-readable JSON

Each pattern includes:
- `id`, `name`, `url` — identity
- `group` — "ui" or "persuasive"
- `category`, `subcategory` — taxonomy
- `problem` — problem summary
- `usage` — list of when-to-use conditions
- `solution` — how to solve
- `rationale` — why it works
- `discussion` — additional considerations
- `example_sites` — referenced example sites
- `votes` — community up/down votes

## Politeness

Default delay between requests is 1.5 seconds. The collector identifies itself via User-Agent. Adjust `--delay` if needed.
