import json
import os
from google import genai
from actions import ALLOWED_ACTIONS

print(os.environ["GEMINI_API_KEY"])
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


SYSTEM_PROMPT = """
You are a deployment risk decision agent.

Rules:
- Choose exactly ONE next action
- Actions must come from the allowed list
- Be conservative with production releases
- Output ONLY valid JSON
- Do NOT include explanations or extra text
"""

def decide_next_action(state):
    print("LLM CALLED")

    allowed_actions = list(ALLOWED_ACTIONS)

    prompt = f"""
Current release state:
- application: {state.application}
- environment: {state.env}
- stage: {state.stage}
- feature_risk: {state.feature_risk}
- service_criticality: {state.service_criticality}
- day_of_week: {state.day_of_week}
- hour_of_day: {state.hour_of_day}
- clash: {state.clash}
- conflicting_service: {state.conflicting_service}

Allowed actions:
{allowed_actions}

Respond with JSON only:
{{ "action": "<one of the allowed actions>" }}
"""

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[
            {"role": "system", "parts": [{"text": SYSTEM_PROMPT}]},
            {"role": "user", "parts": [{"text": prompt}]}
        ],
        config={
            "temperature": 0.0,
            "response_mime_type": "application/json"
        }
    )

    def extract_text(response):
        parts = response.candidates[0].content.parts
        text_parts = [p.text for p in parts if hasattr(p, "text")]
        return "".join(text_parts)

    print("LLM RESPONSE:", response)
    raw_text = extract_text(response)

    try:
        parsed = json.loads(raw_text)
        action = parsed["action"]
    except Exception as e:
        raise ValueError(f"Invalid JSON from Gemini: {raw_text}") from e

    return action
