# Claude Code Integration

## Option 1: As a Claude Code Skill

Copy `.claude/skills/ux-patterns/` directory to your project. The skill will be available automatically when working in that project.

Files needed:
- `.claude/skills/ux-patterns/SKILL.md` — skill instructions
- `.claude/skills/ux-patterns/ux-patterns-index.yaml` — pattern index
- `.claude/skills/ux-patterns/ux-patterns.yaml` — full reference

## Option 2: Via CLAUDE.md

Add to your project's `CLAUDE.md`:

```markdown
## UX Patterns

When designing or reviewing UI, consult the UX pattern knowledge base:
1. Scan `path/to/patterns/ux-patterns-index.yaml` for relevant patterns
2. Look up details in `path/to/patterns/ux-patterns.yaml`
3. Apply pattern solutions while respecting `avoid_when` constraints
```

## Option 3: As a Custom Slash Command

Create `.claude/commands/ux-patterns.md`:

```markdown
Read the UX pattern index from patterns/ux-patterns-index.yaml and find patterns relevant to: $ARGUMENTS

Then look up the full details in patterns/ux-patterns.yaml and recommend the best patterns with implementation guidance.
```

Usage: `/ux-patterns registration flow with social login`
