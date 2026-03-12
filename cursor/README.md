# Cursor / Windsurf / Other IDE Integration

## Cursor

### Option 1: Project Rules

Add to `.cursor/rules`:

```
When designing or prototyping UI, use the UX pattern knowledge base.
1. Scan patterns/ux-patterns-index.yaml to find relevant patterns
2. Read full details from patterns/ux-patterns.yaml
3. Recommend 2-5 patterns with rationale
4. Apply solutions while respecting avoid_when constraints
```

### Option 2: Include as Context

Reference the YAML files in your `.cursorrules` file so they're automatically included in context.

## Windsurf

Add to `.windsurfrules` the same instructions as Cursor Option 1 above.

## Any LLM-powered IDE

The pattern files are standard YAML — include them as context or reference files in whatever tool you use. The `prompts/SYSTEM_PROMPT.md` provides the instructions any LLM needs to use the patterns effectively.
