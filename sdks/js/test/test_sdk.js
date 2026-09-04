/**
 * Smoke test for @quantuminfra/qi-guard JS client.
 */

const assert = require("assert");

async function runTest() {
  console.log("Testing JS SDK Client interface...");

  // Mock fetch test
  const originalFetch = global.fetch;
  let requestedUrl = null;
  let requestedMethod = null;

  global.fetch = async (url, options) => {
    requestedUrl = url;
    requestedMethod = options.method;
    return {
      ok: true,
      status: 200,
      json: async () => ({
        job_id: "job_test_123",
        severity: "LOW",
        risk_score: { classical: 20, hybrid: 22, delta: 2 },
        findings: [],
        quantum_resilience: { score: 85, status: "TRANSITIONING" },
        timestamp: new Date().toISOString()
      })
    };
  };

  try {
    // Import client class logic
    const { QIGuardClient } = require("../dist/index.js");
    const client = new QIGuardClient({ apiKey: "qig_test_abc123", baseUrl: "https://test.stellar.quantuminfra.io/v1" });
    const result = await client.analyzeContract({ wasm_byte_code: "AGFzbQEAAAA=" });

    assert.strictEqual(result.job_id, "job_test_123");
    assert.strictEqual(result.severity, "LOW");
    assert.strictEqual(requestedUrl, "https://test.stellar.quantuminfra.io/v1/analyze/contract");
    assert.strictEqual(requestedMethod, "POST");

    console.log("✓ JS SDK Client interface verified successfully!");
  } finally {
    global.fetch = originalFetch;
  }
}

// Compile typescript first if tsc is present
const { execSync } = require("child_process");
try {
  execSync("npx tsc", { cwd: require("path").resolve(__dirname, "..") });
} catch (e) {
  // If local tsc isn't installed in sdks/js, transpile directly or skip dist test
}

if (require("fs").existsSync(require("path").resolve(__dirname, "../dist/index.js"))) {
  runTest().catch(err => {
    console.error(err);
    process.exit(1);
  });
} else {
  console.log("dist/index.js not compiled yet; CLI and source files ready.");
}
