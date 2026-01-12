import json
import os
from google import genai
from actions import ALLOWED_ACTIONS

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


ACTIONS_BY_STAGE = {
    "START": ["evaluate_risk"],
    "RISK_EVAL": ["check_clash"],
    "SCHEDULING": ["approve_release", "abort_release", "reflect"],
    "REFLECT": ["approve_release", "abort_release"],
}


SYSTEM_PROMPT = """
You are a deployment risk decision agent.

Rules:
- Choose exactly ONE next action
- Actions must come from the allowed list
- Be conservative with production releases
# - Be aggressive and bold with production releases
- Output ONLY valid JSON
- Do NOT include explanations outside the JSON

The JSON MUST contain:
- "action": the chosen action
- "reason": a short explanation for humans
"""

def decide_next_action(state, memory):
    print("LLM CALLED")

    allowed_actions = ACTIONS_BY_STAGE.get(state.stage, ["abort_release"])

    past = memory.episodes()

    memory_hint = ""
    if past:
        memory_hint = "\nHistorical context (advisory only):\n"
        for p in past:
            memory_hint += f"{p}\n"

        
    print("MEMORY HINT:", memory_hint)



    def extract_text(response):
        parts = response.candidates[0].content.parts
        text_parts = [p.text for p in parts if hasattr(p, "text")]
        return "".join(text_parts)

    if state.stage == "REFLECT":
        state.decision = "approve_release" # this is because when we move from approve_release to reflect, we lose the decision.
        reflection_prompt = f"""
    You previously chose the action: {state.decision}

    Given the SAME release state:
    - feature_risk: {state.feature_risk}
    - service_criticality: {state.service_criticality}
    - day_of_week: {state.day_of_week}
    - hour_of_day: {state.hour_of_day}
    - clash: {state.clash}

    Question:
    Is this decision still safe to execute in production?

    Respond with JSON only:
    {{ "confirm": true | false , "reason": "<short explanation for humans>" }}
    """

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[{"role": "system", "parts": [{"text": SYSTEM_PROMPT}]},
                      {"role": "user", "parts": [{"text": reflection_prompt}]}],
            config={
                "temperature": 0.0,
                "response_mime_type": "application/json"
            }
        )

        

        raw = extract_text(response)
        confirm = json.loads(raw).get("confirm", False)
        reason = json.loads(raw).get("reason", False)

        print(f"LLM returned confirm: {confirm}")
        print(f"confirmation reason: {reason}")


        if confirm:
            return state.decision
        else:
            print("REFLECTION OVERRIDE: aborting for safety")
            return "abort_release"




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

{memory_hint}

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

    

    # print("LLM RESPONSE:", response)
    raw_text = extract_text(response)

    try:
        parsed = json.loads(raw_text)
        action = parsed["action"]
        reason = parsed["reason"]

        print(f"LLM returned action: {action}")
        print(f"EXPLANATION: {reason}")


        # Reflection trigger: approval in prod
        if (
            state.env == "prod"
            and action == "approve_release"
        ):
            print("TRIGGERING REFLECTION STEP")
            return "reflect"


    except Exception as e:
        raise ValueError(f"Invalid JSON from Gemini: {raw_text}") from e


    return action
