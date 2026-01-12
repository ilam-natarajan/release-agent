SCENARIO_HIGH_RISK_FRIDAY = {
    "feature_risk": "HIGH",
    "service_criticality": "HIGH",
    "day_of_week": "FRI",
    "hour_of_day": 16,
    "clash_outcomes": [True, False],
    "conflicting_services": ["PAYMENTS-SERVICE"]
}

SCENARIO_LOW_RISK_FRIDAY = {
    "feature_risk": "LOW",
    "service_criticality": "LOW",
    "day_of_week": "FRI",
    "hour_of_day": 16,
    "clash_outcomes": [False],
    "conflicting_services": [""]
}

SCENARIO_LOW_RISK_SATURDAY = {
    "feature_risk": "LOW",
    "service_criticality": "LOW",
    "day_of_week": "SAT",
    "hour_of_day": 16,
    "clash_outcomes": [False],
    "conflicting_services": [""]
}

SCENARIO_LOW_RISK_MONDAY = {
    "feature_risk": "LOW",
    "service_criticality": "LOW",
    "day_of_week": "MON",
    "hour_of_day": 8,
    "clash_outcomes": [False],
    "conflicting_services": [""]
}

SCENARIO_LOW_RISK_WEEKDAY = {
    "feature_risk": "LOW",
    "service_criticality": "MEDIUM",
    "day_of_week": "TUE",
    "hour_of_day": 10,
    "clash_outcomes": [False],
    "conflicting_services": [""]
}
