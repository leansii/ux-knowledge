# UX Pattern Advisor

Knowledge base of 170 UX/UI patterns for interface prototyping and design decisions. Enriched with source data from ui-patterns.com.

## When to Use

Activate this skill when:
- Designing or prototyping any user interface
- Reviewing UI/UX decisions in existing code
- User asks about UX patterns, best practices, or "how to design X"
- Building forms, navigation, onboarding, social features, or data displays
- Need to choose between alternative interaction patterns

## Files

- `ux-patterns-index.yaml` — compact index of all 170 patterns (id, problem, tags). Load this first to find relevant patterns quickly.
- `ux-patterns.yaml` — full reference with all fields below.

## Pattern Fields

Each pattern contains:
- `problem` — concise, action-oriented problem statement
- `source_problem` — original problem description from ui-patterns.com (169/170)
- `when_to_use` — list of situations where the pattern applies
- `solution` — detailed implementation guidance
- `rationale` — why the pattern works psychologically/behaviorally (162/170)
- `discussion` — caveats, nuances, edge cases (58/170)
- `avoid_when` — when NOT to use this pattern
- `related_patterns` — IDs of complementary patterns
- `tags` — categorization for filtering
- `source_url` — link to original pattern page
- `votes` — community up/down votes from source

## Workflow

### 1. Match
Read `ux-patterns-index.yaml` to scan all patterns and identify which ones are relevant to the current task. Use tags and problem descriptions to narrow down candidates.

### 2. Recommend
Look up matched pattern IDs in `ux-patterns.yaml` for full details. Consider:
- Does the `problem` match the user's situation?
- Do `when_to_use` conditions apply?
- Are there `avoid_when` warnings that disqualify this pattern?
- Read `rationale` to understand WHY it works — helps justify recommendations.
- Check `related_patterns` for complementary solutions.

Present 2-5 most relevant patterns with brief rationale for each.

### 3. Implement
When building UI, apply the pattern's `solution` guidance:
- Combine multiple patterns when appropriate (e.g., Wizard + Steps Left + Completeness Meter)
- Respect `avoid_when` constraints
- Check `discussion` for edge cases and caveats

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
