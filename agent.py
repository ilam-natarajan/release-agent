def decide_next_action(state):
    if state.stage == "START":
        return "evaluate_risk"

    if state.stage == "RISK_EVAL":
        return "check_clash"

    if state.stage == "SCHEDULING":
        if state.clash:
            # High-risk + peak time + critical service → no reschedule, abort
            if (
                state.feature_risk == "HIGH"
                and state.service_criticality == "HIGH"
                and state.day_of_week == "FRI"
                and state.hour_of_day >= 15
            ):
                return "abort_release"
            return "reschedule"
        else:
            return "approve_release"

    if state.stage == "DECISION":
        return "approve_release"

    return "finish"
