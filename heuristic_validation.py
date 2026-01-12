ALLOWED_ACTIONS = {"GO", "NO_GO", "DELAY"}

def validate_heuristic(h: dict) -> None:
    assert isinstance(h["when"], dict)
    assert h["recommendation"] in ALLOWED_ACTIONS
    assert 0.0 <= h["confidence"] <= 1.0
    assert h["supporting_episodes"] >= 1

    if h["supporting_episodes"] < 3:
        assert h["confidence"] <= 0.6
