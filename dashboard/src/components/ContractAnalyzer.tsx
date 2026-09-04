import React, { useState } from "react";

interface Finding {
  id: string;
  type: string;
  component: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  evidence: string[];
  remediation: string;
  quantumContribution: boolean;
}

interface ScanResult {
  jobId: string;
  contractId: string;
  classicalScore: number;
  hybridScore: number;
  delta: number;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  pqcScore: number;
  pqcStatus: string;
  findings: Finding[];
}

export const ContractAnalyzer: React.FC = () => {
  const [selectedPreset, setSelectedPreset] = useState("vault_vuln");
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState<ScanResult | null>({
    jobId: "job_cnt_8f9a2b1c",
    contractId: "CCW67TZJTGHVU2E5LILK2BEF2HCH66DY35ZJ3KBAE3B7D6AXDOJ5",
    classicalScore: 71,
    hybridScore: 78,
    delta: 7,
    severity: "HIGH",
    pqcScore: 38,
    pqcStatus: "NOT_READY",
    findings: [
      {
        id: "QIG-SCF-0041",
        type: "ACCESS_CONTROL",
        component: "transfer_admin()",
        severity: "HIGH",
        evidence: [
          "Unrestricted external caller can invoke state modification",
          "Missing env.current_contract_address() / require_auth() validation"
        ],
        remediation: "Ensure address.require_auth() is checked before transferring admin rights.",
        quantumContribution: true
      },
      {
        id: "QIG-SCF-0019",
        type: "UNCHECKED_ARITHMETIC",
        component: "calculate_shares()",
        severity: "MEDIUM",
        evidence: [
          "Potential integer overflow on large deposit amounts prior to division"
        ],
        remediation: "Utilize checked_mul() or i128 wider precision for ratio computation.",
        quantumContribution: false
      }
    ]
  });

  const handleRunScan = async () => {
    setIsScanning(true);

    try {
      // Attempt live call to backend /v1/analyze/contract
      const res = await fetch("/v1/analyze/contract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          wasm_byte_code: "AGFzbQEAAAA=",
          contract_address: "CCW67TZJTGHVU2E5LILK2BEF2HCH66DY35ZJ3KBAE3B7D6AXDOJ5",
          network: "testnet"
        })
      });

      if (res.ok) {
        const data = await res.json();
        setResult({
          jobId: data.job_id,
          contractId: data.contract_id || "CCW67TZJTGHVU2E5LILK2BEF2HCH66DY35ZJ3KBAE3B7D6AXDOJ5",
          classicalScore: data.risk_score.classical,
          hybridScore: data.risk_score.hybrid,
          delta: data.risk_score.delta,
          severity: data.severity,
          pqcScore: data.quantum_resilience.score,
          pqcStatus: data.quantum_resilience.status,
          findings: data.findings.map((f: any) => ({
            id: f.id,
            type: f.type,
            component: f.component || "contract",
            severity: f.severity,
            evidence: f.evidence || [],
            remediation: f.remediation || "",
            quantumContribution: !!f.quantum_contribution
          }))
        });
      } else {
        throw new Error("Backend offline");
      }
    } catch {
      // Simulation preset fallback
      if (selectedPreset === "token_clean") {
        setResult({
          jobId: `job_cnt_${Math.random().toString(36).substring(2, 8)}`,
          contractId: "CB4KRYM6CB7OWQ6TWYRR3TO4CGZMWCCQVDAITJN5Q2Y",
          classicalScore: 12,
          hybridScore: 14,
          delta: 2,
          severity: "LOW",
          pqcScore: 88,
          pqcStatus: "PQC_COMPLIANT",
          findings: []
        });
      } else {
        setResult({
          jobId: `job_cnt_${Math.random().toString(36).substring(2, 8)}`,
          contractId: "CCW67TZJTGHVU2E5LILK2BEF2HCH66DY35ZJ3KBAE3B7D6AXDOJ5",
          classicalScore: 71,
          hybridScore: 78,
          delta: 7,
          severity: "HIGH",
          pqcScore: 38,
          pqcStatus: "NOT_READY",
          findings: [
            {
              id: "QIG-SCF-0041",
              type: "ACCESS_CONTROL",
              component: "transfer_admin()",
              severity: "HIGH",
              evidence: [
                "Unrestricted external caller can invoke state modification",
                "Missing require_auth() validation check in WASM call graph"
              ],
              remediation: "Add address.require_auth() verification prior to executing state mutation.",
              quantumContribution: true
            }
          ]
        });
      }
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Scanner Control Panel */}
      <div className="glass-panel" style={{ padding: "1.5rem" }}>
        <h2 style={{ marginBottom: "0.5rem" }}>Soroban Smart Contract Scanner</h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.875rem", marginBottom: "1.25rem" }}>
          Disassembles Soroban WASM bytecode, extracts opcode call graphs, and applies PennyLane variational quantum circuits to detect high-dimensional vulnerability patterns.
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr auto", gap: "1rem", alignItems: "flex-end" }}>
          <div>
            <label style={{ fontSize: "0.75rem", textTransform: "uppercase", color: "var(--text-dim)", display: "block", marginBottom: "0.35rem" }}>
              Sample Soroban Contract Presets:
            </label>
            <select
              id="contract-preset-select"
              className="input-field"
              value={selectedPreset}
              onChange={(e) => setSelectedPreset(e.target.value)}
            >
              <option value="vault_vuln">Soroban Yield Vault (Vulnerable - Missing Auth Check)</option>
              <option value="token_clean">Soroban Token Standard (Verified - Zero Vulnerabilities)</option>
              <option value="flash_loan">Flash Loan Receiver (High Risk - Reentrancy Surface)</option>
            </select>
          </div>

          <div>
            <label style={{ fontSize: "0.75rem", textTransform: "uppercase", color: "var(--text-dim)", display: "block", marginBottom: "0.35rem" }}>
              Or Enter Stellar Contract Address:
            </label>
            <input
              id="contract-address-input"
              className="input-field mono"
              type="text"
              placeholder="CCW67TZJTGHVU2E5LILK2BEF2HCH66DY35ZJ3KBA..."
              defaultValue="CCW67TZJTGHVU2E5LILK2BEF2HCH66DY35ZJ3KBAE3B7D6AXDOJ5"
            />
          </div>

          <button
            id="run-analysis-btn"
            className="btn btn-primary"
            onClick={handleRunScan}
            disabled={isScanning}
            style={{ height: "42px", padding: "0 1.5rem" }}
          >
            {isScanning ? "Quantum Simulating..." : "⚡ Execute Quantum Audit"}
          </button>
        </div>
      </div>

      {/* Results View */}
      {result && (
        <div className="glass-panel" style={{ padding: "1.5rem" }}>
          {/* Header Bar */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border-subtle)", paddingBottom: "1rem", marginBottom: "1.5rem" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                <h3 style={{ fontSize: "1.25rem" }}>Audit Result: {result.contractId.substring(0, 16)}...</h3>
                <span className={`badge ${result.severity === "HIGH" || result.severity === "CRITICAL" ? "badge-critical" : result.severity === "MEDIUM" ? "badge-high" : "badge-low"}`}>
                  {result.severity} RISK
                </span>
              </div>
              <span style={{ fontSize: "0.8rem", color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>
                Job ID: {result.jobId}
              </span>
            </div>

            <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
              <div style={{ textAlign: "right" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--text-dim)", display: "block" }}>PQC READINESS</span>
                <span style={{ fontWeight: 700, color: result.pqcScore > 70 ? "var(--emerald)" : "var(--amber)" }}>
                  {result.pqcScore}/100 ({result.pqcStatus})
                </span>
              </div>
            </div>
          </div>

          {/* Side-by-Side Score Delta Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1rem", marginBottom: "1.5rem" }}>
            <div className="glass-card">
              <span className="stat-label">Classical MLP Score</span>
              <div style={{ fontSize: "2rem", fontWeight: 800, marginTop: "0.25rem" }}>
                {result.classicalScore}<span style={{ fontSize: "1rem", color: "var(--text-dim)" }}>/100</span>
              </div>
              <p style={{ fontSize: "0.75rem", color: "var(--text-dim)", marginTop: "0.25rem" }}>
                Pure static opcode frequency classifier
              </p>
            </div>

            <div className="glass-card" style={{ borderColor: "var(--border-active)", background: "rgba(99, 102, 241, 0.08)" }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span className="stat-label" style={{ color: "var(--primary-light)" }}>Hybrid Quantum Model</span>
                <span className="badge badge-quantum">PennyLane VQC</span>
              </div>
              <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--cyan)", marginTop: "0.25rem" }}>
                {result.hybridScore}<span style={{ fontSize: "1rem", color: "var(--text-dim)" }}>/100</span>
              </div>
              <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>
                Variational rotation gates feature map
              </p>
            </div>

            <div className="glass-card" style={{ background: "rgba(16, 185, 129, 0.08)", borderColor: "rgba(16, 185, 129, 0.3)" }}>
              <span className="stat-label" style={{ color: "var(--emerald)" }}>Quantum Advantage Delta</span>
              <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--emerald)", marginTop: "0.25rem" }}>
                +{result.delta} <span style={{ fontSize: "1rem" }}>pts</span>
              </div>
              <p style={{ fontSize: "0.75rem", color: "var(--text-dim)", marginTop: "0.25rem" }}>
                Increased sensitivity on subtle call patterns
              </p>
            </div>
          </div>

          {/* Findings List */}
          <h4 style={{ marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            Vulnerability Findings ({result.findings.length})
          </h4>

          {result.findings.length === 0 ? (
            <div style={{ background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.3)", borderRadius: "8px", padding: "1.5rem", textAlign: "center" }}>
              <span style={{ fontSize: "2rem" }}>🛡️</span>
              <h4 style={{ color: "var(--emerald)", marginTop: "0.5rem" }}>Clean Contract</h4>
              <p style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>
                No known Soroban vulnerability patterns or authentication gaps detected.
              </p>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              {result.findings.map((f) => (
                <div key={f.id} className="glass-card" style={{ borderLeft: "4px solid #f43f5e" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <span className="badge badge-critical">{f.severity}</span>
                        <strong style={{ fontSize: "1rem" }}>{f.type}</strong>
                        <code style={{ fontSize: "0.85rem", color: "var(--cyan)" }}>{f.component}</code>
                      </div>
                      <span style={{ fontSize: "0.75rem", color: "var(--text-dim)" }}>Finding ID: {f.id}</span>
                    </div>
                    {f.quantumContribution && (
                      <span className="badge badge-quantum">⚡ Quantum Assisted</span>
                    )}
                  </div>

                  <div style={{ marginBottom: "0.75rem" }}>
                    <span style={{ fontSize: "0.75rem", color: "var(--text-dim)", display: "block", marginBottom: "0.25rem" }}>EVIDENCE:</span>
                    <ul style={{ paddingLeft: "1.25rem", fontSize: "0.85rem", color: "var(--text-muted)" }}>
                      {f.evidence.map((ev, idx) => (
                        <li key={idx}>{ev}</li>
                      ))}
                    </ul>
                  </div>

                  <div style={{ background: "rgba(0,0,0,0.4)", padding: "0.75rem", borderRadius: "6px", border: "1px solid var(--border-subtle)" }}>
                    <span style={{ fontSize: "0.75rem", color: "var(--amber)", fontWeight: 700, display: "block", marginBottom: "0.2rem" }}>
                      RECOMMENDED REMEDIATION:
                    </span>
                    <p style={{ fontSize: "0.85rem", color: "var(--text-main)" }}>{f.remediation}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
