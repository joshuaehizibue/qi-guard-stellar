import React from "react";

interface ProjectOverviewProps {
  tier: string;
  usage: {
    contractsUsed: number;
    contractsLimit: number;
    addressesUsed: number;
    addressesLimit: number;
  };
  onNavigateTab: (tab: string) => void;
}

export const ProjectOverview: React.FC<ProjectOverviewProps> = ({ tier, usage, onNavigateTab }) => {
  const contractPct = usage.contractsLimit === -1 ? 5 : Math.min(100, Math.round((usage.contractsUsed / usage.contractsLimit) * 100));
  const addressPct = usage.addressesLimit === -1 ? 5 : Math.min(100, Math.round((usage.addressesUsed / usage.addressesLimit) * 100));

  return (
    <div>
      {/* Top Stats Cards */}
      <div className="stats-grid">
        <div className="glass-panel stat-card" style={{ padding: "1.25rem" }}>
          <span className="stat-label">Contract Analyses (Monthly)</span>
          <div className="stat-val-row">
            <span className="stat-value">{usage.contractsUsed}</span>
            <span style={{ fontSize: "0.875rem", color: "var(--text-dim)" }}>
              / {usage.contractsLimit === -1 ? "Unlimited" : usage.contractsLimit}
            </span>
          </div>
          <div className="progress-bar-bg">
            <div className="progress-bar-fill" style={{ width: `${contractPct}%` }}></div>
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
            {usage.contractsLimit === -1 ? "Unlimited Protocol quota" : `${100 - contractPct}% remaining this billing cycle`}
          </span>
        </div>

        <div className="glass-panel stat-card" style={{ padding: "1.25rem" }}>
          <span className="stat-label">Address Anomaly Scans</span>
          <div className="stat-val-row">
            <span className="stat-value">{usage.addressesUsed}</span>
            <span style={{ fontSize: "0.875rem", color: "var(--text-dim)" }}>
              / {usage.addressesLimit === -1 ? "Unlimited" : usage.addressesLimit}
            </span>
          </div>
          <div className="progress-bar-bg">
            <div className="progress-bar-fill" style={{ width: `${addressPct}%`, background: "linear-gradient(90deg, #06b6d4 0%, #10b981 100%)" }}></div>
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
            Monitoring Stellar testnet & mainnet accounts
          </span>
        </div>

        <div className="glass-panel stat-card" style={{ padding: "1.25rem" }}>
          <span className="stat-label">Avg Quantum Delta Gain</span>
          <div className="stat-val-row">
            <span className="stat-value" style={{ color: "var(--cyan)" }}>+7.7%</span>
            <span className="badge badge-quantum">PennyLane VQC</span>
          </div>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>
            Variational circuit feature transformation vs pure classical MLP
          </p>
        </div>

        <div className="glass-panel stat-card" style={{ padding: "1.25rem" }}>
          <span className="stat-label">Active Model Version</span>
          <div className="stat-val-row">
            <span className="stat-value" style={{ fontSize: "1.25rem" }}>qi-guard-stellar-0.1.0</span>
          </div>
          <p style={{ fontSize: "0.75rem", color: "var(--emerald)", marginTop: "0.25rem" }}>
            ✓ Model Registry weights verified (SHA-256)
          </p>
        </div>
      </div>

      {/* Quickstart & Integration Center */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem", marginBottom: "2rem" }}>
        <div className="glass-panel" style={{ padding: "1.5rem" }}>
          <h3 style={{ marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span>⚡</span> Quick Audit via CLI
          </h3>
          <p style={{ fontSize: "0.875rem", color: "var(--text-muted)", marginBottom: "1rem" }}>
            Audit your compiled Soroban smart contracts directly from your terminal with zero configuration:
          </p>
          <div style={{ background: "rgba(0,0,0,0.5)", padding: "1rem", borderRadius: "8px", border: "1px solid var(--border-subtle)", marginBottom: "1rem" }}>
            <code style={{ color: "#38bdf8", fontSize: "0.85rem" }}>
              npx @quantuminfra/qi-guard analyze --wasm ./target/release/contract.wasm
            </code>
          </div>
          <button
            id="quickstart-scan-btn"
            className="btn btn-primary"
            onClick={() => onNavigateTab("analyzer")}
          >
            Launch Browser Scanner →
          </button>
        </div>

        <div className="glass-panel" style={{ padding: "1.5rem" }}>
          <h3 style={{ marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span>🤖</span> CI/CD GitHub Action
          </h3>
          <p style={{ fontSize: "0.875rem", color: "var(--text-muted)", marginBottom: "1rem" }}>
            Block vulnerabilities before deployment with automated PR status checks:
          </p>
          <div style={{ background: "rgba(0,0,0,0.5)", padding: "1rem", borderRadius: "8px", border: "1px solid var(--border-subtle)", marginBottom: "1rem" }}>
            <code style={{ color: "#a855f7", fontSize: "0.85rem" }}>
              uses: quantuminfra/qi-guard-action@v1<br />
              with:<br />
              &nbsp;&nbsp;api-key: ${"{"}{"{"} secrets.QIGUARD_API_KEY {"}"}{"}"}<br />
              &nbsp;&nbsp;wasm-path: "contract.wasm"
            </code>
          </div>
          <button
            id="quickstart-keys-btn"
            className="btn btn-secondary"
            onClick={() => onNavigateTab("keys")}
          >
            Generate CI/CD API Key
          </button>
        </div>
      </div>
    </div>
  );
};
