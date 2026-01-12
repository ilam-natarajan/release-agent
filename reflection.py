"""Heuristic extraction from recent episodic memory."""
import json

REFLECTION_PROMPT = """
You are extracting reusable decision heuristics from past episodes.

Episodes:
{episodes}

Rules:
- Only generalise across shared context attributes.
- Do NOT invent new attributes.
- If fewer than 3 supporting episodes exist, confidence MUST be <= 0.6.
- Return JSON only. No explanation.

Output format:
{{
  "heuristics": [
    {{
      "when": {{ "...": "..." }},
      "recommendation": "GO | NO_GO | DELAY",
      "confidence": 0.x,
      "supporting_episodes": n
    }}
  ]
}}
"""


MODEL = "gemini-3-flash-preview"


def run_reflection(client, episodes: list) -> list:
    """Generate heuristic candidates from recent episodes via the LLM."""
    prompt = REFLECTION_PROMPT.format(episodes=json.dumps(episodes, indent=2))

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={"temperature": 0.0, "response_mime_type": "application/json"},
    )

    # Gemini returns structured candidates
    text = response.candidates[0].content.parts[0].text

    parsed = json.loads(text)
    print("REFLECTION OUTPUT:", json.dumps(parsed, indent=2))
    return parsed.get("heuristics", [])
