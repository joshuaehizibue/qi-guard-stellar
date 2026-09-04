#!/usr/bin/env node

/**
 * QI-Guard CLI Tool (npx qi-guard)
 * Quantum-Enhanced Smart Contract Security CLI for Stellar/Soroban
 */

const fs = require("fs");
const path = require("path");

const colors = {
  reset: "\x1b[0m",
  bold: "\x1b[1m",
  dim: "\x1b[2m",
  cyan: "\x1b[36m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  red: "\x1b[31m",
  magenta: "\x1b[35m",
  blue: "\x1b[34m",
};

function banner() {
  console.log(`
${colors.cyan}${colors.bold}⚡ QI-GUARD // QUANTUM SMART CONTRACT SECURITY${colors.reset}
${colors.dim}Stellar Community Fund Build Award — Soroban Security Engine${colors.reset}
`);
}

function printUsage() {
  banner();
  console.log(`
${colors.bold}Usage:${colors.reset}
  npx qi-guard <command> [options]

${colors.bold}Commands:${colors.reset}
  ${colors.green}analyze${colors.reset}      Analyze a Soroban smart contract WASM file or deployed contract
  ${colors.green}resilience${colors.reset}   Audit post-quantum resilience (PQC readiness) for an address
  ${colors.green}benchmark${colors.reset}    Inspect side-by-side classical vs. hybrid quantum ML metrics
  ${colors.green}version${colors.reset}      Show CLI and protocol version

${colors.bold}Options for analyze:${colors.reset}
  --wasm <path>         Path to compiled Soroban .wasm bytecode file
  --address <addr>      Stellar contract address (C...)
  --key <apiKey>        QI-Guard API key (or set QIGUARD_API_KEY env)
  --url <baseUrl>       API base URL (default: https://stellar.quantuminfra.io/v1)
  --json                Output raw JSON response

${colors.bold}Examples:${colors.reset}
  npx qi-guard analyze --wasm ./target/wasm32-unknown-unknown/release/vault.wasm
  npx qi-guard resilience CA3D5KRYM6CB7OWQ6TWYRR3TO4CGZMWCCQVDAITJN5...
  npx qi-guard benchmark job_cnt_8f9a2b1c
`);
}

function parseArgs() {
  const args = process.argv.slice(2);
  const parsed = {
    command: args[0],
    wasm: null,
    address: null,
    key: process.env.QIGUARD_API_KEY || null,
    url: process.env.QIGUARD_API_URL || "https://stellar.quantuminfra.io/v1",
    json: false,
    extra: []
  };

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--wasm" && i + 1 < args.length) {
      parsed.wasm = args[++i];
    } else if (arg === "--address" && i + 1 < args.length) {
      parsed.address = args[++i];
    } else if (arg === "--key" && i + 1 < args.length) {
      parsed.key = args[++i];
    } else if (arg === "--url" && i + 1 < args.length) {
      parsed.url = args[++i];
    } else if (arg === "--json") {
      parsed.json = true;
    } else {
      parsed.extra.push(arg);
    }
  }

  return parsed;
}

async function apiRequest(baseUrl, path, method, body, apiKey) {
  const url = `${baseUrl.replace(/\/+$/, "")}${path}`;
  const headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
  };
  if (apiKey) {
    headers["Authorization"] = `Bearer ${apiKey}`;
  }

  const res = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let err = null;
    try {
      err = await res.json();
    } catch {
      err = await res.text();
    }
    const msg = (err && (err.detail || err.message)) || res.statusText;
    throw new Error(`API Error (${res.status}): ${msg}`);
  }

  return await res.json();
}

function getSeverityColor(sev) {
  switch (sev) {
    case "CRITICAL":
      return colors.red + colors.bold;
    case "HIGH":
      return colors.red;
    case "MEDIUM":
      return colors.yellow;
    case "LOW":
      return colors.green;
    default:
      return colors.reset;
  }
}

async function handleAnalyze(options) {
  let wasmBase64 = null;

  if (options.wasm) {
    const resolvedPath = path.resolve(process.cwd(), options.wasm);
    if (!fs.existsSync(resolvedPath)) {
      console.error(`${colors.red}Error:${colors.reset} WASM file not found at: ${resolvedPath}`);
      process.exit(1);
    }
    const buffer = fs.readFileSync(resolvedPath);
    wasmBase64 = buffer.toString("base64");
  }

  if (!wasmBase64 && !options.address) {
    console.error(`${colors.red}Error:${colors.reset} Please provide either --wasm <file.wasm> or --address <contract_id>`);
    process.exit(1);
  }

  if (!options.json) {
    banner();
    console.log(`${colors.dim}Submitting analysis to:${colors.reset} ${options.url}`);
    console.log(`${colors.dim}Target:${colors.reset} ${options.wasm || options.address}\n`);
  }

  const payload = {};
  if (wasmBase64) payload.wasm_byte_code = wasmBase64;
  if (options.address) payload.contract_address = options.address;

  try {
    const data = await apiRequest(options.url, "/analyze/contract", "POST", payload, options.key);

    if (options.json) {
      console.log(JSON.stringify(data, null, 2));
      return;
    }

    const sevColor = getSeverityColor(data.severity);

    console.log(`┌─────────────────────────────────────────────────────────────┐`);
    console.log(`│ ${colors.bold}CONTRACT SECURITY RISK REPORT${colors.reset}                               │`);
    console.log(`├─────────────────────────────────────────────────────────────┤`);
    console.log(`│ Job ID:             ${data.job_id.padEnd(39)} │`);
    if (data.contract_id) {
      console.log(`│ Contract ID:        ${(data.contract_id.substring(0, 36) + "...").padEnd(39)} │`);
    }
    console.log(`│ Overall Severity:   ${sevColor}${data.severity.padEnd(39)}${colors.reset} │`);
    console.log(`│ Classical Score:    ${String(data.risk_score.classical).padEnd(39)} │`);
    console.log(`│ Hybrid Model Score: ${colors.cyan}${colors.bold}${String(data.risk_score.hybrid).padEnd(39)}${colors.reset} │`);
    console.log(`│ Quantum Delta:      ${colors.green}+${data.risk_score.delta} pts detection sensitivity${colors.reset}           │`);
    console.log(`│ Quantum Resilience: ${String(data.quantum_resilience.score).padEnd(2)}/100 (${data.quantum_resilience.status.padEnd(16)})             │`);
    console.log(`└─────────────────────────────────────────────────────────────┘\n`);

    console.log(`${colors.bold}Detailed Findings (${data.findings.length}):${colors.reset}`);
    if (data.findings.length === 0) {
      console.log(`  ${colors.green}✓ Zero critical vulnerabilities detected.${colors.reset}\n`);
    } else {
      data.findings.forEach((f, idx) => {
        const fc = getSeverityColor(f.severity);
        console.log(`  ${idx + 1}. [${fc}${f.severity}${colors.reset}] ${colors.bold}${f.type}${colors.reset} in ${colors.cyan}${f.component || "contract"}${colors.reset}`);
        console.log(`     ID: ${f.id} | Model: ${f.model_version || "default"} | Quantum Assisted: ${f.quantum_contribution ? colors.green + "YES" : colors.dim + "NO"}${colors.reset}`);
        if (f.evidence && f.evidence.length) {
          f.evidence.forEach(e => console.log(`     • ${colors.dim}${e}${colors.reset}`));
        }
        if (f.remediation) {
          console.log(`     ${colors.yellow}Fix:${colors.reset} ${f.remediation}`);
        }
        console.log("");
      });
    }

    if (data.severity === "HIGH" || data.severity === "CRITICAL" || data.risk_score.hybrid > 75) {
      process.exitCode = 1;
    }
  } catch (err) {
    console.error(`\n${colors.red}Analysis Failed:${colors.reset} ${err.message}`);
    process.exit(1);
  }
}

async function handleResilience(options) {
  const target = options.address || options.extra[0];
  if (!target) {
    console.error(`${colors.red}Error:${colors.reset} Missing target address or contract ID.`);
    process.exit(1);
  }

  try {
    const data = await apiRequest(options.url, `/resilience/${encodeURIComponent(target)}`, "GET", null, options.key);
    if (options.json) {
      console.log(JSON.stringify(data, null, 2));
      return;
    }
    banner();
    console.log(`Target:             ${data.target}`);
    console.log(`Type:               ${data.target_type}`);
    console.log(`Resilience Score:   ${colors.bold}${data.resilience_score}/100${colors.reset}`);
    console.log(`PQC Status:         ${data.status}`);
    console.log(`Key Algorithm:      ${data.key_type}`);
    console.log(`On-chain Exposure:  ${data.exposure_count} ledger transactions\n`);
    console.log(`${colors.bold}Recommendations:${colors.reset}`);
    data.pqc_recommendations.forEach(r => console.log(`  • ${r}`));
  } catch (err) {
    console.error(`\n${colors.red}Resilience Audit Failed:${colors.reset} ${err.message}`);
    process.exit(1);
  }
}

async function handleBenchmark(options) {
  const jobId = options.extra[0];
  if (!jobId) {
    console.error(`${colors.red}Error:${colors.reset} Missing job ID.`);
    process.exit(1);
  }

  try {
    const data = await apiRequest(options.url, `/benchmarks/${encodeURIComponent(jobId)}`, "GET", null, options.key);
    if (options.json) {
      console.log(JSON.stringify(data, null, 2));
      return;
    }
    banner();
    console.log(`Job ID: ${data.job_id}`);
    console.log(`\nClassical Baseline vs. Quantum Hybrid Model:`);
    console.table({
      Classical: {
        Precision: data.classical.precision.toFixed(3),
        Recall: data.classical.recall.toFixed(3),
        "F1 Score": data.classical.f1.toFixed(3),
        "Latency (ms)": data.classical.latency_ms.toFixed(1)
      },
      "Quantum Hybrid": {
        Precision: data.hybrid.precision.toFixed(3),
        Recall: data.hybrid.recall.toFixed(3),
        "F1 Score": data.hybrid.f1.toFixed(3),
        "Latency (ms)": data.hybrid.latency_ms.toFixed(1)
      },
      "Delta / Gain": {
        Precision: (data.hybrid.precision - data.classical.precision >= 0 ? "+" : "") + (data.hybrid.precision - data.classical.precision).toFixed(3),
        Recall: (data.hybrid.recall - data.classical.recall >= 0 ? "+" : "") + (data.hybrid.recall - data.classical.recall).toFixed(3),
        "F1 Score": `+${(data.quantum_delta.f1_improvement * 100).toFixed(1)}%`,
        "Latency (ms)": `+${data.quantum_delta.latency_delta_ms.toFixed(1)}ms`
      }
    });
  } catch (err) {
    console.error(`\n${colors.red}Benchmark Retrieval Failed:${colors.reset} ${err.message}`);
    process.exit(1);
  }
}

async function main() {
  const options = parseArgs();

  switch (options.command) {
    case "analyze":
      await handleAnalyze(options);
      break;
    case "resilience":
      await handleResilience(options);
      break;
    case "benchmark":
      await handleBenchmark(options);
      break;
    case "version":
    case "-v":
    case "--version":
      console.log("0.1.0");
      break;
    case "help":
    case "--help":
    case "-h":
    default:
      printUsage();
      break;
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
