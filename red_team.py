# red_team.py
from typing import TypedDict, List
import json


class RedTeamResult(TypedDict):
    concerns: List[str]
    risk_level: str              # LOW | MEDIUM | HIGH
    suggested_action: str        # NONE | DELAY | NO_GO


RED_TEAM_PROMPT = """
You are a red-team reviewer for a production deployment decision.

Your role:
- Assume the decision could be wrong.
- Look for missing information, risky assumptions, or edge cases.
- Be conservative and adversarial.

Context:
{context}

Decision proposed:
{decision}

Execution evidence (mocked):
{evidence}

Rules:
- If risks are severe or information is missing, suggest DELAY or NO_GO.
- If risks are minor, suggest NONE.
- Do NOT invent facts.
- Return a SINGLE JSON OBJECT (not an array).

Output format:
{{
  "concerns": ["..."],
  "risk_level": "LOW | MEDIUM | HIGH",
  "suggested_action": "NONE | DELAY | NO_GO"
}}
"""

# red_team.py
MODEL = "gemini-3-flash-preview"

def run_red_team(client, context: dict, decision: str, evidence: dict) -> RedTeamResult:
    prompt = RED_TEAM_PROMPT.format(
        context=json.dumps(context, indent=2),
        decision=decision,
        evidence=json.dumps(evidence, indent=2)
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    text = response.candidates[0].content.parts[0].text
    parsed = json.loads(text)

    # ---- HARD NORMALISATION ----
    if isinstance(parsed, list):
        if len(parsed) != 1:
            raise ValueError("Red-team returned multiple results")
        parsed = parsed[0]

    # ---- HARD VALIDATION ----
    assert parsed["risk_level"] in {"LOW", "MEDIUM", "HIGH"}
    assert parsed["suggested_action"] in {"NONE", "DELAY", "NO_GO"}
    assert isinstance(parsed["concerns"], list)

    return parsed
