from state import ReleaseState
from agent import decide_next_action
from simulator import simulate
from memory import EpisodicMemory
from scenarios import SCENARIO_HIGH_RISK_FRIDAY
from scenarios import SCENARIO_LOW_RISK_WEEKDAY
from scenarios import SCENARIO_LOW_RISK_FRIDAY
from scenarios import SCENARIO_LOW_RISK_MONDAY
from scenarios import SCENARIO_LOW_RISK_SATURDAY

def run_release_agent():
    memory = EpisodicMemory()

    state = ReleaseState(
        release_id="ACCOUNT-OPENING-SERVICE-1.0.0",
        application="ACCOUNT-OPENING-SERVICE",
        env="prod"
    )

    scenario = SCENARIO_HIGH_RISK_FRIDAY

    while state.stage not in ["DONE", "ABORTED"]:
        print(f"\nOBSERVE: {state}")
        action = decide_next_action(state, memory)
        print(f"DECIDE: {action}")
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

    outcome = "SUCCESS" if state.decision != "abort_release" else "ABORTED"

    memory.write(
        context=context,
        decision=state.decision,
        outcome=outcome
    )


if __name__ == "__main__":
    run_release_agent()
