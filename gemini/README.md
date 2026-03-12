# Gemini Integration

## Google AI Studio

1. Create a new prompt in AI Studio
2. In the System Instructions, paste the contents of `prompts/SYSTEM_PROMPT.md`
3. Upload both YAML files from `patterns/` as context

## Gemini API

```python
import google.generativeai as genai

# Load pattern files
with open("patterns/ux-patterns-index.yaml") as f:
    index = f.read()
with open("patterns/ux-patterns.yaml") as f:
    patterns = f.read()
with open("prompts/SYSTEM_PROMPT.md") as f:
    system_prompt = f.read()

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=f"{system_prompt}\n\n## Pattern Index\n{index}"
)

# For detailed lookups, include full patterns in context
chat = model.start_chat()
response = chat.send_message("I need help designing a registration flow")
```

## Gemini in Cursor / VS Code

Add to your `.cursorrules` or project instructions:

```
When designing UI, consult these UX pattern files:
- patterns/ux-patterns-index.yaml (scan first)
- patterns/ux-patterns.yaml (detailed lookup)

Follow the workflow in prompts/SYSTEM_PROMPT.md
```
