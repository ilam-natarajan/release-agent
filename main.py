from planner import run_planner
from heuristic_engine import applicable_heuristics
from red_team import run_red_team
from state import ReleaseState
from agent import decide_next_action
from simulator import simulate
from reflection import run_reflection
from heuristic_validation import validate_heuristic
from memory import EpisodicMemory
from scenarios import SCENARIO_HIGH_RISK_FRIDAY
from scenarios import SCENARIO_LOW_RISK_WEEKDAY
from scenarios import SCENARIO_LOW_RISK_FRIDAY
from scenarios import SCENARIO_LOW_RISK_MONDAY
from scenarios import SCENARIO_LOW_RISK_SATURDAY

import os
from google import genai

REFLECTION_WINDOW = 5


client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def run_release_agent():
    memory = EpisodicMemory()

    

    scenario = SCENARIO_LOW_RISK_MONDAY

    state = ReleaseState(
        release_id="ACCOUNT-OPENING-SERVICE-1.0.0",
        application="ACCOUNT-OPENING-SERVICE",
        env="prod",
        day_of_week=scenario["day_of_week"],
        hour_of_day=scenario["hour_of_day"],
        feature_risk=scenario["feature_risk"],
        service_criticality=scenario["service_criticality"]
    )

    while state.stage not in ["DONE", "ABORTED"]:
        print(f"\nOBSERVE: {state}")
        # action = decide_next_action(state, memory)

        # ---- CONTEXT FOR DECISION ----
        context = {
            "feature_risk": state.feature_risk,
            "day_of_week": state.day_of_week,
            "service_criticality": state.service_criticality,
            "clash_detected": scenario["clash_outcomes"],   # <-- from simulation
            "env": state.env

        }

        # ---- APPLY HEURISTICS (NEW) ----
        applicable = applicable_heuristics(
            memory.heuristics(),
            context
        )

        # ---- PLAN (heuristic-aware) ----
        plan = run_planner(
            client=client,
            context=context,
            heuristics=applicable
        )

        print("DEBUG plan:", plan, type(plan))

        action = plan["decision"]
        print(f"DECIDE: {action} | reason: {plan.get('reason')}")


        # ---- EXECUTION EVIDENCE (mocked) ----
        evidence = {
            "clash_detected": context["clash_detected"],
            "freeze_window": False,
            "missing_info": []
        }

        # ---- RED TEAM REVIEW (ADVISORY) ----
        red_team_result = run_red_team(
            client=client,
            context=context,
            decision=plan["decision"],
            evidence=evidence
        )

        print("\nRED TEAM REVIEW (ADVISORY):")
        print(f"Risk level: {red_team_result['risk_level']}")
        for concern in red_team_result["concerns"]:
            print(" -", concern)
        print(f"Suggested action: {red_team_result['suggested_action']}")


        state = simulate(state, action, scenario)

    print(f"\nFINAL DECISION: {state.decision}")
    print("TRACE:")
    for h in state.history:
        print(" ", h)

    context = {
        "feature_risk": state.feature_risk,
        "day_of_week": state.day_of_week,
        "service_criticality": state.service_criticality
    }

    outcome = "SUCCESS" if state.decision != "ABORT" else "ABORTED"

    memory.write(
        context=context,
        decision=state.decision,
        outcome=outcome
    )

    if should_reflect(memory):
        recent = memory.episodes()[-REFLECTION_WINDOW:]
        candidates = run_reflection(client, recent)

        for h in candidates:
            try:
                validate_heuristic(h)
                memory.add_heuristic(h)
            except AssertionError:
                pass


def should_reflect(memory) -> bool:
    return len(memory.episodes()) % REFLECTION_WINDOW == 0


if __name__ == "__main__":
    run_release_agent()
