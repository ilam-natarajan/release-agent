const scenarios = [
  {
    name: "Checkout patch",
    risk: "low",
    service: "payments",
    timing: "Wed 10:30",
    notes: "Small patch, canary ready",
    decision: "GO",
    confidence: 82,
  },
  {
    name: "Inventory refactor",
    risk: "medium",
    service: "fulfillment",
    timing: "Thu 18:45",
    notes: "Potential cache churn, add SRE",
    decision: "DELAY",
    confidence: 67,
  },
  {
    name: "Auth migration",
    risk: "high",
    service: "identity",
    timing: "Fri 16:10",
    notes: "Rollback unclear, high blast radius",
    decision: "NO-GO",
    confidence: 88,
  },
];

const scenarioList = document.getElementById("scenarioList");
const decisionValue = document.getElementById("decisionValue");
const confidenceFill = document.getElementById("confidenceFill");
const confidenceValue = document.getElementById("confidenceValue");
const decisionNotes = document.getElementById("decisionNotes");
const demoStatus = document.getElementById("demoStatus");
const steps = Array.from(document.querySelectorAll(".pipeline-step"));
const runButton = document.getElementById("runDemo");
const resetButton = document.getElementById("resetDemo");
const pulseButton = document.getElementById("pulseBtn");

let selectedScenario = scenarios[0];
let running = false;
let timeouts = [];

function renderScenarios() {
  scenarioList.innerHTML = "";
  scenarios.forEach((scenario) => {
    const card = document.createElement("button");
    card.className = "scenario";
    card.type = "button";
    card.innerHTML = `
      <strong>${scenario.name}</strong><br />
      <span>${scenario.service}</span><br />
      <span>${scenario.timing}</span>
    `;
    if (scenario === selectedScenario) {
      card.classList.add("selected");
    }
    card.addEventListener("click", () => {
      if (running) {
        return;
      }
      selectedScenario = scenario;
      renderScenarios();
      decisionNotes.textContent = `${scenario.notes} (Risk: ${scenario.risk}).`;
      decisionValue.textContent = "Awaiting run";
      confidenceFill.style.width = "0%";
      confidenceValue.textContent = "0%";
      demoStatus.textContent = "Idle";
    });
    scenarioList.appendChild(card);
  });
}

function clearPipeline() {
  steps.forEach((step) => step.classList.remove("active", "done"));
}

function clearTimers() {
  timeouts.forEach((timeoutId) => clearTimeout(timeoutId));
  timeouts = [];
}

function setDecision() {
  const { decision, confidence, notes } = selectedScenario;
  decisionValue.textContent = decision;
  confidenceFill.style.width = `${confidence}%`;
  confidenceValue.textContent = `${confidence}%`;
  decisionNotes.textContent = `Decision notes: ${notes}.`;
}

function runDemo() {
  if (running) {
    return;
  }
  running = true;
  demoStatus.textContent = "Running";
  clearPipeline();
  decisionValue.textContent = "Analyzing";
  confidenceFill.style.width = "0%";
  confidenceValue.textContent = "0%";
  decisionNotes.textContent = "Pipeline in progress...";

  steps.forEach((step, index) => {
    const activateId = setTimeout(() => {
      step.classList.add("active");
    }, index * 600);
    const doneId = setTimeout(() => {
      step.classList.remove("active");
      step.classList.add("done");
      if (index === steps.length - 1) {
        setDecision();
        demoStatus.textContent = "Complete";
        running = false;
      }
    }, index * 600 + 420);
    timeouts.push(activateId, doneId);
  });
}

function resetDemo() {
  running = false;
  clearTimers();
  clearPipeline();
  decisionValue.textContent = "Awaiting run";
  confidenceFill.style.width = "0%";
  confidenceValue.textContent = "0%";
  demoStatus.textContent = "Idle";
  decisionNotes.textContent = "Select a scenario, then run the demo to see the pipeline light up.";
}

function pulseSignal() {
  document.body.classList.add("signal");
  setTimeout(() => document.body.classList.remove("signal"), 600);
}

runButton.addEventListener("click", runDemo);
resetButton.addEventListener("click", resetDemo);
pulseButton.addEventListener("click", pulseSignal);

renderScenarios();
resetDemo();
