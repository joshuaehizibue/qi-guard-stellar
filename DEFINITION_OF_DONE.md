# Definition of Done (DoD) — QI-Guard for Stellar MVP

This document outlines the mandatory quality bars and completion criteria across feature stories, API modules, and release milestones for **QI-Guard for Stellar MVP**.

---

## 1. Project-Wide Quality Bar

Every deliverable shipped in QI-Guard MUST satisfy the following criteria:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DEFINITION OF DONE CHECKLIST                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  [ ] Code Quality: Clean pass on ruff/black (Python) and clippy (Rust).     │
│  [ ] Test Coverage: Minimum 85% branch coverage on core ML & parsing code.   │
│  [ ] Benchmark Delta: Side-by-side classical vs. hybrid output present.     │
│  [ ] API Contract: Strict compliance with OpenAPI 3.0 specification.        │
│  [ ] Latency SLA: Sub-500ms p95 latency for REST API analysis endpoints.    │
│  [ ] Security: Zero hardcoded secrets; API keys validated & rate-limited.    │
│  [ ] Documentation: SDK quickstart functional in < 5 minutes.                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Story-Level Acceptance Criteria Template

For any backlog story to be marked as **Completed**, it must satisfy:

1. **Functional Completeness:** Implementation matches the specified Gherkin user story acceptance criteria.
2. **Automated Testing:**
   - Unit tests covering edge cases (e.g., malformed WASM binaries, empty Horizon ledger responses, quantum circuit convergence failures).
   - Integration test added to CI/CD verifying endpoint behavior against testnet.
3. **API Contract Verification:** Response JSON schemas strictly match `API_CONTRACT.md`.
4. **Documentation & Types:** TypeScript/Python SDK typings updated and exported.

---

## 3. Module-Specific DoD Standards

### 3.1 WASM Parser & Contract Risk Module
- [ ] Successfully parses Soroban WASM binaries without crashing on valid WebAssembly specs.
- [ ] Correctly identifies missing `require_auth()` calls and flags uninitialized admin keys.
- [ ] Computes static feature vector in under 50ms for WASM files up to 2MB.

### 3.2 Hybrid Quantum-Classical Engine
- [ ] PennyLane variational quantum circuit executes parameter-shift gradient step cleanly without simulation divergence.
- [ ] Quantum Delta (`hybrid_score - classical_score`) is explicitly calculated and recorded in the database.
- [ ] Model weights are version-tagged and logged in the PostgreSQL Model Registry schema.

### 3.3 Behavioral Anomaly Engine
- [ ] Ingests Horizon transaction streams with auto-retry and exponential backoff on HTTP 429/503.
- [ ] Correctly builds temporal address interaction subgraphs for 7-day lookback windows.
- [ ] Isolation Forest baseline and hybrid quantum anomaly scores output calibrated risk levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).

### 3.4 Quantum Resilience Module
- [ ] Scans Ed25519/Secp256k1 key usage and public key exposure frequency across Stellar ledgers.
- [ ] Evaluates cryptographic agility against NIST PQC migration standards.

---

## 4. Release & Launch DoD (MVP Definition)

QI-Guard for Stellar MVP is ready for public release and SCF submission when:

- [ ] A developer can sign up at `stellar.quantuminfra.io` and generate an operational API key in under **2 minutes**.
- [ ] A developer can install `@quantuminfra/qi-guard` (npm) or `qi-guard` (PyPI) and analyze a Soroban contract in under **5 minutes**.
- [ ] Every API response includes transparent classical vs. hybrid model benchmarks.
- [ ] GitHub Action `quantuminfra/qi-guard-action` can block PRs based on a `severity: HIGH` contract vulnerability threshold.
- [ ] Complete benchmark report comparing QI-Guard against Scout benchmark results is published.
