/**
 * QI-Guard GitHub Action Runner.
 * Executes contract WASM static & hybrid quantum analysis and enforces CI/CD quality gates.
 */

const fs = require("fs");
const path = require("path");

function getInput(name, defaultValue = "") {
  const val = process.env[`INPUT_${name.replace(/ /g, "_").toUpperCase()}`] ||
              process.env[`INPUT_${name.replace(/-/g, "_").toUpperCase()}`] ||
              process.env[`INPUT_${name}`];
  return (val !== undefined && val !== "") ? val.trim() : defaultValue;
}

function setOutput(key, value) {
  const outputPath = process.env.GITHUB_OUTPUT;
  if (outputPath && fs.existsSync(outputPath)) {
    fs.appendFileSync(outputPath, `${key}=${value}\n`);
  } else {
    console.log(`[OUTPUT] ${key}=${value}`);
  }
}

function appendSummary(markdown) {
  const summaryPath = process.env.GITHUB_STEP_SUMMARY;
  if (summaryPath) {
    fs.appendFileSync(summaryPath, markdown + "\n\n");
  }
}

const SEVERITY_RANKS = {
  NONE: 0,
  LOW: 1,
  MEDIUM: 2,
  HIGH: 3,
  CRITICAL: 4
};

async function run() {
  const apiKey = getInput("api-key");
  const wasmPath = getInput("wasm-path");
  const contractAddress = getInput("contract-address");
  const failSeverity = getInput("fail-severity", "HIGH").toUpperCase();
  const failScore = parseInt(getInput("fail-score", "75"), 10);
  const apiUrl = getInput("api-url", "https://stellar.quantuminfra.io/v1").replace(/\/+$/, "");

  console.log("⚡ Initiating QI-Guard Soroban Smart Contract Security Analysis...");

  if (!wasmPath && !contractAddress) {
    console.error("::error::Either wasm-path or contract-address input must be provided.");
    process.exit(1);
  }

  let wasmBase64 = null;
  if (wasmPath) {
    const fullPath = path.resolve(process.cwd(), wasmPath);
    if (!fs.existsSync(fullPath)) {
      console.error(`::error::WASM binary not found at ${fullPath}`);
      process.exit(1);
    }
    const buffer = fs.readFileSync(fullPath);
    wasmBase64 = buffer.toString("base64");
    console.log(`Loaded WASM artifact: ${wasmPath} (${(buffer.length / 1024).toFixed(1)} KB)`);
  }

  const payload = {
    wasm_byte_code: wasmBase64,
    contract_address: contractAddress || undefined,
    network: "testnet"
  };

  const headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
  };
  if (apiKey) {
    headers["Authorization"] = `Bearer ${apiKey}`;
  }

  const response = await fetch(`${apiUrl}/analyze/contract`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    let err = "";
    try {
      err = JSON.stringify(await response.json());
    } catch {
      err = response.statusText;
    }
    console.error(`::error::QI-Guard API request failed (${response.status}): ${err}`);
    process.exit(1);
  }

  const report = await response.json();

  // Export Action outputs
  setOutput("risk-score", report.risk_score.hybrid);
  setOutput("severity", report.severity);
  setOutput("findings-count", report.findings.length);
  setOutput("quantum-delta", report.risk_score.delta);
  setOutput("pqc-score", report.quantum_resilience.score);

  // Markdown Summary
  const isPassedSeverity = (SEVERITY_RANKS[report.severity] || 0) < (SEVERITY_RANKS[failSeverity] || 99);
  const isPassedScore = report.risk_score.hybrid <= failScore;
  const isGatePassed = isPassedSeverity && isPassedScore;

  let summaryMd = `## 🛡️ QI-Guard Security Gate Report\n\n`;
  summaryMd += `**Status:** ${isGatePassed ? "✅ **PASSED**" : "❌ **FAILED (Gate Breach)**"}\n\n`;
  summaryMd += `| Metric | Classical Baseline | Quantum Hybrid Model | Delta Gain |\n`;
  summaryMd += `| :--- | :--- | :--- | :--- |\n`;
  summaryMd += `| **Risk Score** | ${report.risk_score.classical}/100 | **${report.risk_score.hybrid}/100** | **+${report.risk_score.delta} pts** |\n`;
  summaryMd += `| **Severity Rating** | — | **${report.severity}** | Threshold: \`${failSeverity}\` |\n`;
  summaryMd += `| **NIST PQC Readiness** | — | **${report.quantum_resilience.score}/100** (\`${report.quantum_resilience.status}\`) | Agility Score |\n\n`;

  if (report.findings.length > 0) {
    summaryMd += `### 🔍 Detected Vulnerability Findings (${report.findings.length})\n\n`;
    summaryMd += `| Severity | Type | Component | Quantum Assisted | Remediation |\n`;
    summaryMd += `| :--- | :--- | :--- | :--- | :--- |\n`;
    report.findings.forEach(f => {
      summaryMd += `| **${f.severity}** | \`${f.type}\` | \`${f.component || "contract"}\` | ${f.quantum_contribution ? "⚡ Yes" : "No"} | ${f.remediation || "Review code"} |\n`;
    });
  } else {
    summaryMd += `> ✅ **No vulnerability patterns detected in the analyzed Soroban bytecode.**\n`;
  }

  appendSummary(summaryMd);

  console.log(`\n======================================================`);
  console.log(`  QI-GUARD ANALYSIS RESULT: ${isGatePassed ? "PASSED" : "FAILED"}`);
  console.log(`  Hybrid Risk Score: ${report.risk_score.hybrid}/100 (Threshold: ${failScore})`);
  console.log(`  Severity: ${report.severity} (Threshold: ${failSeverity})`);
  console.log(`  Quantum Delta: +${report.risk_score.delta} detection sensitivity`);
  console.log(`======================================================\n`);

  if (!isGatePassed) {
    if (!isPassedSeverity) {
      console.error(`::error::Security gate failed! Contract severity '${report.severity}' exceeds maximum allowed '${failSeverity}'.`);
    }
    if (!isPassedScore) {
      console.error(`::error::Security gate failed! Contract risk score '${report.risk_score.hybrid}' exceeds threshold '${failScore}'.`);
    }
    process.exit(1);
  }
}

run().catch(err => {
  console.error(`::error::Unexpected failure in QI-Guard Action: ${err.message}`);
  process.exit(1);
});
