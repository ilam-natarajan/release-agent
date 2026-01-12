# heuristics.py
from typing import TypedDict, Dict


class Heuristic(TypedDict):
    when: Dict[str, str]
    recommendation: str
    confidence: float
    supporting_episodes: int
