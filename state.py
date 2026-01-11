from dataclasses import dataclass, field
from typing import List

@dataclass
class ReleaseState:
    release_id: str
    application: str
    env: str

    stage: str = "START"  
    # START → RISK_EVAL → SCHEDULING → DECISION → DONE / ABORTED

    # Risk signals
    feature_risk: str = "UNKNOWN"     # LOW / MEDIUM / HIGH
    service_criticality: str = "UNKNOWN"  # LOW / MEDIUM / HIGH

    # Time context
    day_of_week: str = "UNKNOWN"  # MON ... SUN
    hour_of_day: int = -1         # 0–23

    # Clash context
    clash: str = "UNKNOWN"        # UNKNOWN / TRUE / FALSE
    conflicting_service: str = ""

    # Outcome
    decision: str = "UNDECIDED"   # GO / DELAY / ABORT
    history: List[str] = field(default_factory=list)
