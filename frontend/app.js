const scenarioSelect = document.getElementById("scenarioSelect");
const scenarioDetails = document.getElementById("scenarioDetails");
const runButton = document.getElementById("runDemo");
const resetButton = document.getElementById("resetDemo");
const logOutput = document.getElementById("logOutput");
const rawOutput = document.getElementById("rawOutput");
const decisionBox = document.getElementById("decisionBox");
const decisionMeta = document.getElementById("decisionMeta");
const reflectionBox = document.getElementById("reflectionBox");
const pipelineSteps = Array.from(document.querySelectorAll("#pipelineSteps li"));
const serverStatus = document.getElementById("serverStatus");
const runStatus = document.getElementById("runStatus");

let scenarios = [];
let running = false;

function setStatus(text) {
  runStatus.textContent = text;
}

function setServerStatus(text) {
  serverStatus.textContent = text;
}

function updateScenarioDetails(scenario) {
  if (!scenario) {
    scenarioDetails.textContent = "No scenario loaded.";
    return;
  }
  const { data } = scenario;
  scenarioDetails.textContent = `Risk: ${data.feature_risk} | Criticality: ${data.service_criticality} | Day: ${data.day_of_week} @ ${data.hour_of_day}:00 | Clash: ${data.clash_outcomes[0]}`;
}

function resetPipeline() {
  pipelineSteps.forEach((step) => step.classList.remove("active", "done"));
}

function highlightPipeline(index) {
  pipelineSteps.forEach((step, i) => {
    step.classList.toggle("active", i === index);
    step.classList.toggle("done", i < index);
  });
}

function markPipelineDone() {
  pipelineSteps.forEach((step) => step.classList.add("done"));
  pipelineSteps.forEach((step) => step.classList.remove("active"));
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function animatePipeline() {
  for (let i = 0; i < pipelineSteps.length; i += 1) {
    highlightPipeline(i);
    await delay(320);
  }
  markPipelineDone();
}

function updateDecision(decision) {
  decisionBox.classList.remove("good", "warn");
  decisionBox.querySelector(".decision-label").textContent = decision || "Awaiting run";
  if (decision === "GO") {
    decisionBox.classList.add("good");
  } else if (decision) {
    decisionBox.classList.add("warn");
  }
}

function formatLog(data) {
  const lines = [];
  data.steps.forEach((step, index) => {
    lines.push(`Step ${index + 1}: ${step.action}`);
    lines.push(`  Planner decision: ${step.plan.decision}`);
    lines.push(`  Reason: ${step.plan.reason}`);
    lines.push(`  Red team: ${step.red_team.risk_level} (${step.red_team.suggested_action})`);
    if (step.red_team.concerns.length) {
      lines.push("  Concerns:");
      step.red_team.concerns.forEach((concern) => lines.push(`    - ${concern}`));
    }
  });
  lines.push(`Final: ${data.decision}`);
  return lines.join("\n");
}

async function fetchScenarios() {
  try {
    const response = await fetch("/api/scenarios");
    if (!response.ok) {
      throw new Error("Failed to load scenarios");
    }
    const payload = await response.json();
    scenarios = payload.scenarios;
    scenarioSelect.innerHTML = "";
    scenarios.forEach((scenario) => {
      const option = document.createElement("option");
      option.value = scenario.id;
      option.textContent = scenario.label;
      scenarioSelect.appendChild(option);
    });
    updateScenarioDetails(scenarios[0]);
    setServerStatus("Server: connected");
  } catch (error) {
    setServerStatus("Server: unavailable (run main.py --serve)");
    scenarioDetails.textContent = "Start the API server to load scenarios.";
  }
}

async function runDemo() {
  if (running) {
    return;
  }
  const scenarioId = scenarioSelect.value;
  if (!scenarioId) {
    return;
  }
  running = true;
  setStatus("Running");
  resetPipeline();
  updateDecision("Running...");
  decisionMeta.textContent = "Confidence: --";
  reflectionBox.textContent = "Running reflection checks...";
  logOutput.textContent = "Executing pipeline...";
  rawOutput.textContent = "{}";

  const pipelineAnimation = animatePipeline();
  try {
    const response = await fetch(`/api/run?scenario=${encodeURIComponent(scenarioId)}`);
    if (!response.ok) {
      const message = await response.text();
      throw new Error(message || "Run failed");
    }
    const data = await response.json();
    await pipelineAnimation;
    updateDecision(data.decision);
    decisionMeta.textContent = `History entries: ${data.history.length}`;
    reflectionBox.textContent = data.reflection.ran
      ? `Reflection ran. Heuristics added: ${data.reflection.added}`
      : "Reflection not triggered.";
    logOutput.textContent = formatLog(data);
    rawOutput.textContent = JSON.stringify(data, null, 2);
    setStatus("Complete");
  } catch (error) {
    logOutput.textContent = `Error: ${error.message}`;
    rawOutput.textContent = "{}";
    setStatus("Failed");
  } finally {
    running = false;
  }
}

function resetDemo() {
  running = false;
  resetPipeline();
  updateDecision("Awaiting run");
  decisionMeta.textContent = "Confidence: --";
  reflectionBox.textContent = "No reflection run yet.";
  logOutput.textContent = "Start the demo to see structured output.";
  rawOutput.textContent = "{}";
  setStatus("Idle");
}

scenarioSelect.addEventListener("change", (event) => {
  const scenario = scenarios.find((item) => item.id === event.target.value);
  updateScenarioDetails(scenario);
});

runButton.addEventListener("click", runDemo);
resetButton.addEventListener("click", resetDemo);

fetchScenarios();
resetDemo();
