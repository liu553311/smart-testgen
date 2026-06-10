# Prompt Design

## Overview

smart-testgen uses a carefully crafted Jinja2 template to instruct LLMs to generate high-quality test cases. This document explains the design rationale.

## Template Strategy

### Role Priming

The prompt begins with: *"You are an expert software tester with deep experience in test design techniques including equivalence partitioning, boundary value analysis, decision tables, state transitions, and error guessing."*

**Why:** Setting the role context primes the LLM to apply professional testing techniques rather than generating only surface-level happy-path tests. Without this, models tend to produce generic "login works" tests without boundary or negative cases.

### Technique Explicit Callout

The prompt explicitly names testing techniques: equivalence partitioning, boundary value analysis, decision tables, state transitions, error guessing.

**Why:** Mentioning specific techniques triggers the LLM to apply them. For example, "boundary value analysis" prompts the model to think about min/max/just-over/just-under values. Without these keywords, models default to basic functional testing.

### Category-Driven Coverage

The template dynamically injects the requested test categories:

```
{% for cat in categories %}   - {{ cat }}
{% endfor %}
```

**Why:** Users can focus on specific test types via `--categories functional,boundary`. When all categories are included, the prompt guides the LLM to distribute test cases across all types, ensuring comprehensive coverage.

### Priority Guidance

The prompt provides explicit prioritization rules:

```
4. Prioritize:
   - Happy-path functional tests (critical/high priority)
   - Boundary value analysis at input limits
   - Negative tests (invalid input, missing fields, wrong types)
   - Edge cases (empty inputs, maximum length, special characters)
   - Security-relevant tests (injection, auth bypass) when applicable
```

**Why:** Without explicit priority guidance, LLMs assign arbitrary priorities. This ordering ensures that functional tests (most business-critical) get higher priority, while edge cases get appropriate (usually lower) priority.

### JSON Schema Enforcement

The prompt includes the exact output JSON schema inline:

```json
{
  "title": "string",
  "test_cases": [
    {
      "id": "TC-001",
      "title": "string",
      ...
    }
  ]
}
```

**Why:** Providing the schema inline is far more reliable than describing the format in prose. Both Claude and GPT-4-class models follow inline schemas with high fidelity. This eliminates most parsing failures.

### "Return ONLY valid JSON" Instruction

The prompt explicitly states: *"Return ONLY valid JSON matching this exact schema, with no explanation before or after."*

**Why:** LLMs naturally want to add conversational wrappers ("Here are the test cases you requested:..."). This instruction minimizes that. The `_extract_json()` fallback in the code handles residual cases.

## Parsing Fallbacks

Despite the prompt, LLMs sometimes wrap JSON in markdown fences (` ```json ... ``` `). The `TestGenerator._extract_json()` method handles three cases:

1. **Markdown-fenced JSON** — regex extraction from ` ```json ... ``` `
2. **JSON with surrounding text** — find first `{` to last `}`
3. **Raw JSON** — direct parse

## Future Enhancements

- **Few-shot examples** — include 1-2 sample test cases in the prompt for higher quality
- **System message** — for Anthropic, use a separate system message with project context
- **Template variants** — security-focused, API-focused, UI-focused templates
- **Chain-of-thought** — ask the model to reason about test design before generating
