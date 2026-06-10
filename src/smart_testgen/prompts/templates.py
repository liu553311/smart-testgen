"""Prompt templates for test case generation."""

DEFAULT_TEMPLATE = """You are an expert software tester with deep experience in test design \
techniques including equivalence partitioning, boundary value analysis, decision tables, \
state transitions, and error guessing.

Your task: generate comprehensive test cases from the following requirements.

## Requirements
{{ requirements }}

## Instructions
1. Generate exactly {{ num_cases }} test cases.
2. Cover these test categories as appropriate for the requirements:
{% for cat in categories %}   - {{ cat }}
{% endfor %}
3. For each test case, provide:
   - A unique ID in the format TC-NNN (starting at TC-001)
   - A concise, descriptive title
   - A detailed description of what is being tested
   - Priority: critical, high, medium, or low
   - Category: one of the listed categories
   - Preconditions (list of strings; use [] if none)
   - Numbered test steps, each with an action and expected result
   - Expected results (list of overall expected outcomes)
   - Tags relevant to the requirement area

4. Prioritize:
   - Happy-path functional tests (critical/high priority)
   - Boundary value analysis at input limits
   - Negative tests (invalid input, missing fields, wrong types)
   - Edge cases (empty inputs, maximum length, special characters)
   - Security-relevant tests (injection, auth bypass) when applicable

## Output Format
Return ONLY valid JSON matching this exact schema, with no explanation before or after:

{
  "title": "string - suite title derived from requirements",
  "test_cases": [
    {
      "id": "TC-001",
      "title": "string",
      "description": "string",
      "priority": "critical|high|medium|low",
      "category": "functional|boundary|negative|edge_case|security|performance|usability|accessibility",
      "preconditions": ["string"],
      "steps": [
        {"step_number": 1, "action": "string", "expected_result": "string"}
      ],
      "expected_results": ["string"],
      "tags": ["string"]
    }
  ]
}

Important: wrap the entire response in a single JSON object.
Do not include markdown fences or any text outside the JSON."""

# Template registry for future extensibility
TEMPLATES: dict[str, str] = {
    "default": DEFAULT_TEMPLATE,
}
