import React, { useState, useEffect } from "react";
import { Navbar } from "./components/Navbar";
import { ProjectOverview } from "./components/ProjectOverview";
import { KeyManager } from "./components/KeyManager";
import { ContractAnalyzer } from "./components/ContractAnalyzer";
import { BenchmarkVisualizer } from "./components/BenchmarkVisualizer";
import { BillingPlans } from "./components/BillingPlans";

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState("overview");
  const [tier, setTier] = useState("DEVELOPER");
  const [usage, setUsage] = useState({
    contractsUsed: 14,
    contractsLimit: 50,
    addressesUsed: 28,
    addressesLimit: 100
  });

  const handleTierUpdated = (newTier: string) => {
    setTier(newTier);
    if (newTier === "BUILDER") {
      setUsage(prev => ({ ...prev, contractsLimit: 500, addressesLimit: 2000 }));
    } else if (newTier === "PROTOCOL") {
      setUsage(prev => ({ ...prev, contractsLimit: -1, addressesLimit: 20000 }));
    }
  };

  useEffect(() => {
    // Attempt fetching live usage
    fetch("/v1/billing/usage?project_id=test_project")
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data) {
          setTier(data.tier || "DEVELOPER");
          setUsage({
            contractsUsed: data.contracts?.used ?? 14,
            contractsLimit: data.contracts?.limit ?? 50,
            addressesUsed: data.addresses?.used ?? 28,
            addressesLimit: data.addresses?.limit ?? 100
          });
        }
      })
      .catch(() => {});
  }, []);

  return (
    <div className="app-container">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} tier={tier} />

      <main>
        {activeTab === "overview" && (
          <ProjectOverview tier={tier} usage={usage} onNavigateTab={setActiveTab} />
        )}
        {activeTab === "analyzer" && <ContractAnalyzer />}
        {activeTab === "benchmarks" && <BenchmarkVisualizer />}
        {activeTab === "keys" && <KeyManager />}
        {activeTab === "billing" && (
          <BillingPlans currentTier={tier} onTierUpdated={handleTierUpdated} />
        )}
      </main>
    </div>
  );
};

export default App;
