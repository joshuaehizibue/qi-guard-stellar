import React from "react";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  tier: string;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, tier }) => {
  return (
    <nav className="navbar glass-panel">
      <div className="nav-brand">
        <div className="logo-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            <path d="M12 8v4" />
            <path d="M12 16h.01" />
          </svg>
        </div>
        <div>
          <h2 style={{ fontSize: "1.25rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            QI-GUARD
            <span style={{ fontSize: "0.7rem", color: "var(--cyan)", fontWeight: 500, letterSpacing: "0.08em" }}>STELLAR/SOROBAN</span>
          </h2>
        </div>
      </div>

      <div className="nav-tabs">
        <button
          id="nav-tab-overview"
          className={`nav-tab-btn ${activeTab === "overview" ? "active" : ""}`}
          onClick={() => setActiveTab("overview")}
        >
          Overview
        </button>
        <button
          id="nav-tab-analyzer"
          className={`nav-tab-btn ${activeTab === "analyzer" ? "active" : ""}`}
          onClick={() => setActiveTab("analyzer")}
        >
          Contract Scanner
        </button>
        <button
          id="nav-tab-benchmarks"
          className={`nav-tab-btn ${activeTab === "benchmarks" ? "active" : ""}`}
          onClick={() => setActiveTab("benchmarks")}
        >
          Quantum Benchmarks
        </button>
        <button
          id="nav-tab-keys"
          className={`nav-tab-btn ${activeTab === "keys" ? "active" : ""}`}
          onClick={() => setActiveTab("keys")}
        >
          API Keys
        </button>
        <button
          id="nav-tab-billing"
          className={`nav-tab-btn ${activeTab === "billing" ? "active" : ""}`}
          onClick={() => setActiveTab("billing")}
        >
          Billing & Tiers
        </button>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
        <span className="badge badge-quantum" id="active-tier-badge">
          {tier} TIER
        </span>
        <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontSize: "0.8rem", color: "var(--text-muted)" }}>
          <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "var(--emerald)", display: "inline-block", boxShadow: "0 0 8px #10b981" }}></span>
          Testnet Online
        </div>
      </div>
    </nav>
  );
};
