def build_decision_summary(
    context: dict,
    planner: dict,
    red_team: dict,
    final_decision: str,
    human_outcome: str
) -> str:
    """
    This text is what gets embedded and indexed.
    It must be concise, narrative, and stable.
    """
    return f"""
Release context:
- Environment: prod
- Feature risk: {context.get("feature_risk")}
- Day of week: {context.get("day_of_week")}
- Service criticality: {context.get("service_criticality")}

Planner decision:
- Decision: {planner["decision"]}
- Reason: {planner.get("reason")}

Red-team review:
- Risk level: {red_team["risk_level"]}
- Concerns: {", ".join(red_team["concerns"])}

Final decision:
- Action taken: {final_decision}

Human-reported outcome after deployment:
- Outcome: {human_outcome}
""".strip()
