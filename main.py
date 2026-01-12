"""Run the release agent and serve the demo UI/API."""
import argparse
import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from google import genai
from agent import decide_next_action
from heuristic_engine import applicable_heuristics
from heuristic_validation import validate_heuristic
from memory import EpisodicMemory
from planner import run_planner
from red_team import run_red_team
from reflection import run_reflection
from scenarios import (
    SCENARIO_HIGH_RISK_FRIDAY,
    SCENARIO_LOW_RISK_FRIDAY,
    SCENARIO_LOW_RISK_MONDAY,
    SCENARIO_LOW_RISK_SATURDAY,
    SCENARIO_LOW_RISK_WEEKDAY,
)
from simulator import simulate
from state import ReleaseState

REFLECTION_WINDOW = 5
FRONTEND_DIR = Path(__file__).parent / "frontend"


def get_client():
    """Create a Gemini client using the configured API key."""
    api_key = os.environ["GEMINI_API_KEY"]
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    return genai.Client(api_key=api_key)


def build_scenarios():
    """Return the scenario registry used by the demo UI and CLI."""
    return {
        "low-risk-monday": ("Low risk Monday", SCENARIO_LOW_RISK_MONDAY),
        "low-risk-weekday": ("Low risk weekday", SCENARIO_LOW_RISK_WEEKDAY),
        "low-risk-friday": ("Low risk Friday", SCENARIO_LOW_RISK_FRIDAY),
        "low-risk-saturday": ("Low risk Saturday", SCENARIO_LOW_RISK_SATURDAY),
        "high-risk-friday": ("High risk Friday", SCENARIO_HIGH_RISK_FRIDAY),
    }


def normalize_action(decision: str) -> str:
    """Map planner decisions to simulator actions."""
    if decision == "GO":
        return "GO"
    if decision == "DELAY":
        return "reschedule"
    if decision == "NO_GO":
        return "abort_release"
    return decision


def run_release_agent(scenario: dict, verbose: bool = True) -> dict:
    """Run the release agent loop for a scenario and return structured results."""
    memory = EpisodicMemory()
    client = get_client()

    state = ReleaseState(
        release_id="ACCOUNT-OPENING-SERVICE-1.0.0",
        application="ACCOUNT-OPENING-SERVICE",
        env="prod",
        day_of_week=scenario["day_of_week"],
        hour_of_day=scenario["hour_of_day"],
        feature_risk=scenario["feature_risk"],
        service_criticality=scenario["service_criticality"],
    )

    steps = []

    while state.stage not in ["DONE", "ABORTED"]:
        if verbose:
            print(f"\nOBSERVE: {state}")
        # action = decide_next_action(state, memory)

        # ---- CONTEXT FOR DECISION ----
        context = {
            "feature_risk": state.feature_risk,
            "day_of_week": state.day_of_week,
            "service_criticality": state.service_criticality,
            "clash_detected": scenario["clash_outcomes"],  # <-- from simulation
            "env": state.env,
        }

        # ---- APPLY HEURISTICS (NEW) ----
        applicable = applicable_heuristics(
            memory.heuristics(),
            context,
        )

        # ---- PLAN (heuristic-aware) ----
        plan = run_planner(
            client=client,
            context=context,
            heuristics=applicable,
        )

        decision = plan["decision"]
        action = normalize_action(decision)
        if verbose:
            print("DEBUG plan:", plan, type(plan))
            print(f"DECIDE: {decision} | reason: {plan.get('reason')}")

        # ---- EXECUTION EVIDENCE (mocked) ----
        evidence = {
            "clash_detected": context["clash_detected"],
            "freeze_window": False,
            "missing_info": [],
        }

        # ---- RED TEAM REVIEW (ADVISORY) ----
        red_team_result = run_red_team(
            client=client,
            context=context,
            decision=plan["decision"],
            evidence=evidence,
        )

        if verbose:
            print("\nRED TEAM REVIEW (ADVISORY):")
            print(f"Risk level: {red_team_result['risk_level']}")
            for concern in red_team_result["concerns"]:
                print(" -", concern)
            print(f"Suggested action: {red_team_result['suggested_action']}")

        steps.append(
            {
                "context": context,
                "heuristics": applicable,
                "plan": plan,
                "red_team": red_team_result,
                "action": action,
                "stage": state.stage,
            }
        )

        state = simulate(state, action, scenario)

    if verbose:
        print(f"\nFINAL DECISION: {state.decision}")
        print("TRACE:")
        for h in state.history:
            print(" ", h)

    context = {
        "feature_risk": state.feature_risk,
        "day_of_week": state.day_of_week,
        "service_criticality": state.service_criticality,
    }

    outcome = "SUCCESS" if state.decision != "ABORT" else "ABORTED"

    memory.write(
        context=context,
        decision=state.decision,
        outcome=outcome,
    )

    reflection_added = 0
    reflection_ran = False
    if should_reflect(memory):
        reflection_ran = True
        recent = memory.episodes()[-REFLECTION_WINDOW:]
        candidates = run_reflection(client, recent)

        for h in candidates:
            try:
                validate_heuristic(h)
                memory.add_heuristic(h)
                reflection_added += 1
            except AssertionError:
                pass

    return {
        "decision": state.decision,
        "history": state.history,
        "steps": steps,
        "reflection": {"ran": reflection_ran, "added": reflection_added},
    }


def should_reflect(memory) -> bool:
    """Return True when the reflection window boundary is reached."""
    return len(memory.episodes()) % REFLECTION_WINDOW == 0


def list_scenarios() -> list:
    """Format scenarios for the demo API response."""
    scenarios = build_scenarios()
    return [
        {"id": key, "label": label, "data": data}
        for key, (label, data) in scenarios.items()
    ]


def resolve_scenario(scenario_id: str) -> dict:
    """Return the scenario data for a given ID, falling back to the first."""
    scenarios = build_scenarios()
    if scenario_id in scenarios:
        return scenarios[scenario_id][1]
    return next(iter(scenarios.values()))[1]


class ReleaseAgentHandler(BaseHTTPRequestHandler):
    """HTTP handler that serves the demo UI and API endpoints."""
    def _send_json(self, payload: dict, status: int = 200) -> None:
        """Send a JSON response with CORS enabled."""
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, payload: str, status: int = 200) -> None:
        """Send a plain-text response."""
        body = payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, path: str) -> None:
        """Serve a static asset from the frontend directory."""
        if path in {"", "/"}:
            path = "/index.html"
        file_path = (FRONTEND_DIR / path.lstrip("/")).resolve()
        if not str(file_path).startswith(str(FRONTEND_DIR.resolve())):
            self._send_text("Not found", status=404)
            return
        if not file_path.exists() or not file_path.is_file():
            self._send_text("Not found", status=404)
            return
        content_type, _ = mimetypes.guess_type(str(file_path))
        content_type = content_type or "application/octet-stream"
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        """Route API calls and static asset requests."""
        parsed = urlparse(self.path)
        if parsed.path == "/api/scenarios":
            self._send_json({"scenarios": list_scenarios()})
            return
        if parsed.path == "/api/run":
            params = parse_qs(parsed.query)
            scenario_id = params.get("scenario", [None])[0]
            try:
                scenario = resolve_scenario(scenario_id)
                result = run_release_agent(scenario, verbose=False)
                result["scenario_id"] = scenario_id
                result["scenario"] = scenario
                self._send_json(result)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
            return
        self._serve_file(parsed.path)


def serve(host: str, port: int) -> None:
    """Start the demo HTTP server."""
    server = ThreadingHTTPServer((host, port), ReleaseAgentHandler)
    print(f"Serving demo UI at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Release agent demo runner")
    parser.add_argument("--serve", action="store_true", help="Serve the demo UI")
    parser.add_argument("--scenario", choices=build_scenarios().keys())
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    if args.serve:
        serve(args.host, args.port)
    else:
        scenario = resolve_scenario(args.scenario)
        run_release_agent(scenario, verbose=not args.quiet)
