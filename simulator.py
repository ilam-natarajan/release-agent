def simulate(state, action, scenario):
    state.history.append(f"ACTION: {action}")

    if action == "evaluate_risk":
        state.feature_risk = scenario["feature_risk"]
        state.service_criticality = scenario["service_criticality"]
        state.day_of_week = scenario["day_of_week"]
        state.hour_of_day = scenario["hour_of_day"]
        state.stage = "RISK_EVAL"

    elif action == "check_clash":
        state.clash = scenario["clash_outcomes"][0]
        state.conflicting_service = scenario["conflicting_services"][0]
        state.stage = "SCHEDULING"

    elif action == "reschedule":
        state.clash = False
        state.stage = "DECISION"

    elif action == "approve_release":
        state.decision = "GO"
        state.stage = "DONE"

    elif action == "abort_release":
        state.decision = "ABORT"
        state.stage = "ABORTED"

    elif action == "finish":
        state.stage = "DONE"

    return state
