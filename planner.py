"""LLM planner that proposes deployment decisions."""
import json

PLANNER_PROMPT = """
You are a deployment decision planner.

Context:
{context}

Applicable heuristics:
{heuristics}

Rules:
- If a heuristic applies, you MUST follow its recommendation unless there is a strong reason not to.
- If you override a heuristic, explain why.
- Be conservative with production releases
- Return JSON only.
- Produce EXACTLY ONE decision.


Output format (single object only):
{{
  "decision": "GO | NO_GO | DELAY",
  "reason": "short explanation"
}}
"""

MODEL = "gemini-3-flash-preview"


def run_planner(client, context: dict, heuristics: list) -> dict:
    """Ask the LLM to return a deployment decision and short rationale."""
    prompt = PLANNER_PROMPT.format(
        context=json.dumps(context, indent=2),
        heuristics=json.dumps(heuristics, indent=2),
    )

    response = client.models.generate_content(
        model=MODEL, contents=prompt, config={"response_mime_type": "application/json"}
    )

    # print("PLANNER RESPONSE:", response)

    text = response.candidates[0].content.parts[0].text
    print("PLANNER OUTPUT:", json.loads(text))
    return json.loads(text)
