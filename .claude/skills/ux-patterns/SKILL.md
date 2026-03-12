# UX Pattern Advisor

Knowledge base of 170 UX/UI patterns for interface prototyping and design decisions.

## When to Use

Activate this skill when:
- Designing or prototyping any user interface
- Reviewing UI/UX decisions in existing code
- User asks about UX patterns, best practices, or "how to design X"
- Building forms, navigation, onboarding, social features, or data displays
- Need to choose between alternative interaction patterns

## Files

- `ux-patterns-index.yaml` — compact index of all 170 patterns (id, problem, tags). Load this first to find relevant patterns quickly.
- `ux-patterns.yaml` — full reference with detailed problem descriptions, when to use, solutions, anti-patterns, and related patterns.

## Workflow

### 1. Match
Read `ux-patterns-index.yaml` to scan all patterns and identify which ones are relevant to the current task. Use tags and problem descriptions to narrow down candidates.

### 2. Recommend
Look up matched pattern IDs in `ux-patterns.yaml` for full details. Consider:
- Does the `problem` match the user's situation?
- Do `when_to_use` conditions apply?
- Are there `avoid_when` warnings that disqualify this pattern?
- Check `related_patterns` for complementary solutions.

Present 2-5 most relevant patterns with brief rationale for each.

### 3. Implement
When building UI, apply the pattern's `solution` guidance:
- Use the pattern name in code comments for traceability
- Combine multiple patterns when appropriate (e.g., Wizard + Steps Left + Completeness Meter)
- Respect `avoid_when` constraints

## Example Queries

- "I need a registration flow" → LazyRegistration, AccountRegistration, Wizard, StepsLeft
- "How to show search results?" → LiveFilter, Autocomplete, Pagination, ContinuousScrolling
- "Users don't complete the form" → GoodDefaults, ForgivingFormat, Autosave, InputFeedback, CompletenessMeter
- "How to onboard new users?" → Guided-tour, coachmarks, BlankSlate, inline-hints, playthrough
- "Need to increase engagement" → Variable-rewards, Achievements, ActivityStream, Levels, Competition

## Tags Reference

Common tags for filtering:
- **input**: forms, fields, user input
- **navigation**: menus, tabs, breadcrumbs
- **data**: tables, search, filtering
- **social**: community, sharing, reputation
- **onboarding**: first-time experience, guidance
- **persuasion**: behavioral design, motivation
- **gamification**: rewards, achievements, progress
- **cognition**: biases, decision-making
- **feedback**: notifications, progress, responses
- **commerce**: shopping, pricing, payments
