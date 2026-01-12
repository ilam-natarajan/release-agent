"""Typed schema helpers for heuristic records."""
from typing import Dict, TypedDict


class Heuristic(TypedDict):
    """Typed dictionary schema for learned decision heuristics."""
    when: Dict[str, str]
    recommendation: str
    confidence: float
    supporting_episodes: int
