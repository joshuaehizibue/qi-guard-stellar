import React, { useState } from "react";

interface ApiKeyItem {
  id: string;
  name: string;
  prefix: string;
  type: "LIVE" | "TEST" | "CI";
  scopes: string[];
  created: string;
  fullKey?: string;
}

export const KeyManager: React.FC = () => {
  const [keys, setKeys] = useState<ApiKeyItem[]>([
    {
      id: "key_1",
      name: "GitHub Actions CI Gate",
      prefix: "qig_ci_9f82...",
      type: "CI",
      scopes: ["contract:analyze"],
      created: "2026-09-01",
      fullKey: "qig_ci_9f82a1b4c6e83d72b5f104e9c8a7b6d5"
    },
    {
      id: "key_2",
      name: "Stellar Testnet Bot",
      prefix: "qig_test_e34b...",
      type: "TEST",
      scopes: ["contract:analyze", "behavior:analyze", "resilience:read"],
      created: "2026-09-02",
      fullKey: "qig_test_e34bc78a1290fe3456789012abcdef34"
    }
  ]);

  const [newKeyName, setNewKeyName] = useState("");
  const [newKeyType, setNewKeyType] = useState<"LIVE" | "TEST" | "CI">("CI");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [latestCreatedKey, setLatestCreatedKey] = useState<string | null>(null);

  const handleCreateKey = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKeyName.trim()) return;

    const prefixMap = {
      LIVE: "qig_live_",
      TEST: "qig_test_",
      CI: "qig_ci_"
    };

    const randomHex = Array.from({ length: 32 }, () => Math.floor(Math.random() * 16).toString(16)).join("");
    const generatedKey = `${prefixMap[newKeyType]}${randomHex}`;

    const newKey: ApiKeyItem = {
      id: `key_${Date.now()}`,
      name: newKeyName.trim(),
      prefix: `${generatedKey.substring(0, 12)}...`,
      type: newKeyType,
      scopes: newKeyType === "CI" ? ["contract:analyze"] : ["contract:analyze", "behavior:analyze", "resilience:read"],
      created: new Date().toISOString().split("T")[0],
      fullKey: generatedKey
    };

    setKeys([newKey, ...keys]);
    setLatestCreatedKey(generatedKey);
    setNewKeyName("");
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleRevoke = (id: string) => {
    setKeys(keys.filter(k => k.id !== id));
  };

  return (
    <div className="glass-panel" style={{ padding: "1.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h2>API Key Management</h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>
            Generate and manage scoped authentication keys for REST API and CI/CD pipelines.
          </p>
        </div>
      </div>

      {latestCreatedKey && (
        <div style={{ background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.3)", borderRadius: "8px", padding: "1rem", marginBottom: "1.5rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <span style={{ color: "var(--emerald)", fontWeight: 700, fontSize: "0.875rem" }}>NEW KEY GENERATED:</span>
              <p style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Copy this key now. For security, it will not be displayed again in full.</p>
            </div>
            <button
              id="copy-new-key-btn"
              className="btn btn-primary"
              onClick={() => copyToClipboard(latestCreatedKey, "new_created")}
            >
              {copiedId === "new_created" ? "✓ Copied!" : "Copy Key"}
            </button>
          </div>
          <code style={{ display: "block", marginTop: "0.5rem", background: "#000", padding: "0.5rem", borderRadius: "4px", color: "#34d399", fontSize: "0.85rem" }}>
            {latestCreatedKey}
          </code>
        </div>
      )}

      {/* Create Key Form */}
      <form onSubmit={handleCreateKey} style={{ display: "flex", gap: "0.75rem", marginBottom: "2rem", background: "rgba(0,0,0,0.25)", padding: "1rem", borderRadius: "8px" }}>
        <input
          id="key-name-input"
          className="input-field"
          type="text"
          placeholder="Key Name (e.g. GitHub Actions Production Scan)"
          value={newKeyName}
          onChange={(e) => setNewKeyName(e.target.value)}
          style={{ flex: 2 }}
        />
        <select
          id="key-type-select"
          className="input-field"
          value={newKeyType}
          onChange={(e) => setNewKeyType(e.target.value as any)}
          style={{ flex: 1 }}
        >
          <option value="CI">CI Key (qig_ci_)</option>
          <option value="TEST">Testnet Key (qig_test_)</option>
          <option value="LIVE">Live Key (qig_live_)</option>
        </select>
        <button id="generate-key-submit-btn" type="submit" className="btn btn-cyan">
          + Generate Key
        </button>
      </form>

      {/* Keys Table */}
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Prefix</th>
              <th>Scopes</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {keys.map((k) => (
              <tr key={k.id}>
                <td style={{ fontWeight: 600 }}>{k.name}</td>
                <td>
                  <span className={`badge ${k.type === "LIVE" ? "badge-critical" : k.type === "CI" ? "badge-medium" : "badge-low"}`}>
                    {k.type}
                  </span>
                </td>
                <td><code style={{ color: "var(--cyan)" }}>{k.prefix}</code></td>
                <td>
                  {k.scopes.map((s) => (
                    <span key={s} style={{ fontSize: "0.75rem", background: "rgba(255,255,255,0.06)", padding: "2px 6px", borderRadius: "4px", marginRight: "4px" }}>
                      {s}
                    </span>
                  ))}
                </td>
                <td style={{ color: "var(--text-dim)" }}>{k.created}</td>
                <td>
                  <div style={{ display: "flex", gap: "0.5rem" }}>
                    {k.fullKey && (
                      <button
                        id={`copy-btn-${k.id}`}
                        className="btn btn-secondary"
                        style={{ padding: "0.3rem 0.6rem", fontSize: "0.75rem" }}
                        onClick={() => copyToClipboard(k.fullKey!, k.id)}
                      >
                        {copiedId === k.id ? "✓ Copied" : "Copy"}
                      </button>
                    )}
                    <button
                      id={`revoke-btn-${k.id}`}
                      className="btn btn-danger"
                      style={{ padding: "0.3rem 0.6rem", fontSize: "0.75rem" }}
                      onClick={() => handleRevoke(k.id)}
                    >
                      Revoke
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
