# heuristic_engine.py

CONFIDENCE_THRESHOLD = 0.6

def heuristic_applies(heuristic: dict, context: dict) -> bool:
    for key, value in heuristic["when"].items():
        if context.get(key) != value:
            return False
    return True


def applicable_heuristics(heuristics: list, context: dict) -> list:
    return [
        h for h in heuristics
        if h["confidence"] >= CONFIDENCE_THRESHOLD
        and heuristic_applies(h, context)
    ]
