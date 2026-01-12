# release-agent

# release-agent

An AI-powered deployment decision agent that learns from experience to make safe production release decisions for humans

## Overview

The release agent simulates a production deployment pipeline and uses LLMs (Gemini) to make context-aware release decisions. It learns from past deployments by extracting heuristics and validates decisions through red-team review.

## Key Features

- **Episodic Memory**: Stores past release decisions and outcomes in [`memory.json`](memory.json)
- **Heuristic Learning**: Automatically extracts decision patterns from historical data using [`reflection.py`](reflection.py)
- **Risk Assessment**: Evaluates feature risk, service criticality, timing, and conflicts
- **Red Team Review**: Advisory adversarial review of decisions via [`red_team.py`](red_team.py)
- **Reflection Loop**: Self-validates high-risk production decisions in [`agent.py`](agent.py)

## How It Works

1. **Context Evaluation**: Assesses release context (risk, day of week, service criticality)
2. **Heuristic Matching**: Applies learned patterns from [`heuristic_engine.py`](heuristic_engine.py)
3. **Decision Planning**: Uses LLM planner with [`planner.py`](planner.py) to decide GO/NO_GO/DELAY
4. **Red Team Review**: Independent adversarial review flags concerns
5. **Reflection**: Production approvals trigger safety confirmation
6. **Memory Update**: Records decision and outcome for future learning

## Usage

```bash
export GEMINI_API_KEY=your_key_here
python main.py
```

The agent runs through a simulated release scenario defined in [`scenarios.py`](scenarios.py) and makes decisions based on learned heuristics and LLM reasoning.

## Demo UI

The demo UI runs from the same process and calls the real pipeline over HTTP.

### Launch the UI

```bash
export GEMINI_API_KEY=your_key_here
python main.py --serve
```

Then open `http://127.0.0.1:8000`.

### Use the UI

1. Pick a scenario from the dropdown.
2. Click **Run** to execute the pipeline.
3. Review the decision, reflection status, and full log output.

### API endpoints

- `GET /api/scenarios` returns scenario metadata for the UI.
- `GET /api/run?scenario=<id>` runs the pipeline for the selected scenario.

## Components

- [`state.py`](state.py) - Release state tracking
- [`agent.py`](agent.py) - Core decision-making logic
- [`planner.py`](planner.py) - LLM-based planning
- [`simulator.py`](simulator.py) - Deployment simulation
- [`memory.py`](memory.py) - Episodic memory management
- [`heuristic_engine.py`](heuristic_engine.py) - Pattern matching
- [`reflection.py`](reflection.py) - Heuristic extraction
- [`red_team.py`](red_team.py) - Adversarial review
- [`heuristic_validation.py`](heuristic_validation.py) - Heuristic constraints

## License

MIT License - see [`LICENSE`](LICENSE)
