import json
from pathlib import Path

MEMORY_FILE = Path("memory.json")

class EpisodicMemory:
    def __init__(self):
        if MEMORY_FILE.exists():
            self.entries = json.loads(MEMORY_FILE.read_text())
        else:
            self.entries = []

    def write(self, context, decision, outcome):
        entry = {
            "context": context,
            "decision": decision,
            "outcome": outcome
        }
        self.entries.append(entry)
        MEMORY_FILE.write_text(json.dumps(self.entries, indent=2))

    def recall(self, context):
        return [
            e for e in self.entries
            if e["context"]["feature_risk"] == context["feature_risk"]
            and e["context"]["day_of_week"] == context["day_of_week"]
        ]
