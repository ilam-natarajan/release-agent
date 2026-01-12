"""Persist episodic memory and learned heuristics to disk."""
import json
from datetime import datetime, timezone
from pathlib import Path

MEMORY_FILE = Path("memory.json")


class EpisodicMemory:
    """Persisted memory store for episodes and extracted heuristics."""
    def __init__(self):
        """Load memory state from disk into process memory."""
        self.memory = self._load()

    def _load(self) -> dict:
        """Read the memory file, handling legacy list formats."""
        if not MEMORY_FILE.exists():
            return {"episodes": [], "heuristics": []}

        data = json.loads(MEMORY_FILE.read_text())

        # migration safety: old list-based memory
        if isinstance(data, list):
            return {"episodes": data, "heuristics": []}

        return data

    def _save(self) -> None:
        """Persist the in-memory state to the memory file."""
        MEMORY_FILE.write_text(json.dumps(self.memory, indent=2))

    # ---------- WRITE ----------

    def write(self, context: dict, decision: str, outcome: str) -> None:
        """Append a new episode entry with context and outcome."""
        entry = {
            "context": context,
            "decision": decision,
            "outcome": outcome,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self.memory["episodes"].append(entry)
        self._save()

    # ---------- READ ----------

    def episodes(self) -> list:
        """Return the list of stored episode records."""
        return self.memory["episodes"]

    def heuristics(self) -> list:
        """Return the list of stored heuristics."""
        return self.memory["heuristics"]

    def add_heuristic(self, heuristic: dict) -> None:
        """Append a validated heuristic and persist it."""
        print("ADDING HEURISTIC TO MEMORY:", heuristic)
        self.memory["heuristics"].append(heuristic)
        self._save()
