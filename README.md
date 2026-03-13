# UX Knowledge

Knowledge base of 170 UX/UI patterns for AI-assisted interface design. Works with any LLM provider — Claude, Gemini, GPT, or local models.

## What's Inside

**170 patterns** covering:
- **UI Design**: Forms, Navigation, Data Display, Social, Commerce, Onboarding
- **Persuasive Design**: Cognitive Biases, Gamification, Attention & Memory, Feedback Timing, Social Influence

Each pattern includes: problem statement, when to use, solution, when to avoid, related patterns, and tags.

## Structure

```
patterns/
  ux-patterns-index.yaml    # Compact index — load into context first (~740 lines)
  ux-patterns.yaml           # Full reference — look up specific patterns (~2670 lines)
prompts/
  SYSTEM_PROMPT.md           # Generic system prompt for any LLM
claude/                      # Claude Code integration guide
gemini/                      # Gemini integration guide
cursor/                      # Cursor/Windsurf/IDE integration guide
.claude/skills/ux-patterns/  # Ready-to-use Claude Code skill
collector/                   # Scraper to collect raw data from ui-patterns.com
```

## Quick Start

### Any LLM (API or chat)
1. Include `prompts/SYSTEM_PROMPT.md` as system instructions
2. Load `patterns/ux-patterns-index.yaml` into context
3. Reference `patterns/ux-patterns.yaml` for detailed lookups

### Claude Code
Copy `.claude/skills/ux-patterns/` to your project. The skill activates automatically when you work on UI.

### Cursor / IDE
See `cursor/README.md` for `.cursorrules` integration.

### Gemini
See `gemini/README.md` for AI Studio and API integration.

## How It Works

1. **Match** — scan the index to find patterns relevant to your task
2. **Recommend** — read full details, check applicability and constraints
3. **Implement** — apply pattern solutions, combine complementary patterns

## Collector

Scrape raw pattern data from the source:

```bash
cd collector
uv run collect.py           # Collect all 170 patterns
uv run collect.py --dry-run # Preview without fetching
```

See `collector/README.md` for full options.

## Pattern Sources

Patterns are based on well-established UX/UI concepts catalogued at [ui-patterns.com](https://ui-patterns.com/patterns), described in our own words.

## License

MIT
