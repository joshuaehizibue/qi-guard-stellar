# Product Backlog — QI-Guard for Stellar MVP

**Goal:** Deliver a quantum-enhanced smart contract security API and SDK for the Stellar/Soroban ecosystem to win the Stellar Community Fund (SCF) Build Award and onboard 100 developer integrations.  
**Assumptions:** 16-week build timeline, 2-week sprint iterations, core engineering stack (FastAPI, PyTorch, PennyLane, PostgreSQL, Redis, React, Rust WASM disassembler).

---

## Epic 1: Core Platform & Foundation (Phase 0 — Weeks 1–3)

| ID | User Story | Priority | Est. | Depends on | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **B1.1** | As a developer, I want a FastAPI service boilerplate with JWT & API key authentication, so that I can securely query QI-Guard endpoints. | High | M | — | Generates `qig_live_`, `qig_test_`, and `qig_ci_` key types with scope checks. |
| **B1.2** | As an engineer, I want PostgreSQL database schemas for projects, contracts, findings, and benchmark runs, so that data persists reliably. | High | M | B1.1 | SQL migrations set up; foreign keys for project API keys and findings established. |
| **B1.3** | As an engineer, I want Redis integration for API rate limiting and Celery background job processing, so that the API remains responsive under load. | High | M | B1.1 | Enforces Developer (50/mo), Builder (500/mo), and Protocol tier limits. |
| **B1.4** | As an ingestion pipeline, I want Stellar Horizon API client routines, so that address transaction history and ledger data can be fetched. | High | L | B1.1 | Ingests payment flows, contract calls; handles cursor pagination & 429 retries. |
| **B1.5** | As an ingestion pipeline, I want a Soroban RPC client module, so that deployed contract WASM bytecodes and ledger state can be retrieved. | High | L | B1.1 | Retrieves bytecode and contract storage entries by contract address (`C...`). |
| **B1.6** | As a static analysis engine, I want a Rust-based WASM parser (`wasmparser` + `pyo3`), so that WASM disassembles into control-flow graphs and function calls. | High | L | — | Extracts opcodes, imports, exports, and flags missing `require_auth()` checks. |

---

## Epic 2: Intelligence Engine & Quantum Pipeline (Phase 1 — Weeks 4–7)

| ID | User Story | Priority | Est. | Depends on | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **B2.1** | As a ML engineer, I want a classical Gradient Boosting / MLP classifier for contract vulnerabilities, so that static WASM features map to risk scores. | High | L | B1.6 | Trained on Soroban security taxonomy dataset; outputs 0–100 base score. |
| **B2.2** | As a quantum ML engineer, I want a PennyLane variational quantum circuit layer on top of PyTorch embeddings, so that quantum feature transformation is applied. | High | XL | B2.1 | `n_qubits = min(8, max(2, features))`; parameter-shift differentiation enabled. |
| **B2.3** | As a security engineer, I want a side-by-side Quantum Benchmark Engine, so that every request calculates classical vs. hybrid score deltas. | High | M | B2.2 | Measures precision, recall, F1, latency (ms), and logs `quantum_contribution` boolean. |
| **B2.4** | As a security analyst, I want a Behavioral Anomaly Engine using isolation forests & temporal address feature vectors, so that suspicious activity is flagged. | High | L | B1.4 | Computes transaction velocity, value concentration, and rapid wallet drain patterns. |
| **B2.5** | As a security researcher, I want a Quantum Resilience scanner for Ed25519 public key surfaces and PQC migration readiness, so that quantum threat scores are generated. | High | M | B1.4 | Evaluates key rotation policies and public key exposure count across ledgers. |
| **B2.6** | As an MLOps engineer, I want an immutable Model Registry in Postgres & S3, so that trained model versions (`qi-guard-stellar-0.1.0`) and weights are versioned. | High | M | B2.3 | Stores SHA-256 weight hashes, quantum gate configurations, and dataset hashes. |

---

## Epic 3: Developer API, SDKs & Dashboard (Phase 2 — Weeks 8–10)

| ID | User Story | Priority | Est. | Depends on | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **B3.1** | As a developer, I want `POST /v1/analyze/contract` and `POST /v1/analyze/behavioral` REST endpoints, so that I can submit audit jobs over HTTP. | High | M | B2.3, B2.4 | Conforms strictly to `API_CONTRACT.md` and returns structured JSON reports. |
| **B3.2** | As a developer, I want `GET /v1/resilience/{target}` and `GET /v1/benchmarks/{job_id}` endpoints, so that I can inspect resilience and quantum deltas. | High | S | B2.5, B2.3 | Returns RFC 7807 error responses on invalid targets or unauthorized API keys. |
| **B3.3** | As a JS/TS developer, I want `@quantuminfra/qi-guard` npm SDK package, so that I can integrate security checks in Node.js / frontend apps. | High | M | B3.1 | Full TypeScript typings, automatic retry handling, and CLI command binary (`npx qi-guard`). |
| **B3.4** | As a Python developer, I want `qi-guard` PyPI package, so that I can run contract analysis directly from Python scripts. | High | M | B3.1 | Clean Pythonic SDK with async/await support and typed dataclass responses. |
| **B3.5** | As a DevOps engineer, I want a GitHub Action (`quantuminfra/qi-guard-action`), so that WASM analysis runs automatically on every pull request. | High | M | B3.3 | Fails build pipeline if `severity == HIGH` or `risk_score > 75`. |
| **B3.6** | As a developer, I want a React developer dashboard, so that I can view projects, API keys, findings, and interactive benchmark comparison graphs. | Medium | L | B3.2 | Built with React, Tailwind CSS, Recharts for side-by-side benchmark charts. |
| **B3.7** | As a business lead, I want Stripe billing integration for Developer (Free), Builder ($49/mo), and Protocol ($199/mo) tiers, so that users can subscribe. | Medium | M | B1.3 | Webhook handler updates usage quotas and project tier permissions automatically. |

---

## Epic 4: Ecosystem Integration & SCF Launch (Phase 3 — Weeks 11–16)

| ID | User Story | Priority | Est. | Depends on | Notes & Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **B4.1** | As a marketing lead, I want production deployment at `stellar.quantuminfra.io`, so that developers can access the live service. | High | M | B3.6 | Automated AWS ECS deployment, SSL, CloudFront CDN, and RDS Postgres replication. |
| **B4.2** | As a product manager, I want to onboard 10 Soroban design partner projects, so that real-world contract feedback is gathered prior to public submission. | High | L | B4.1 | Design partners provided complimentary Protocol tier access; telemetry collected. |
| **B4.3** | As a security scientist, I want a published "QI-Guard vs. Scout" comparative benchmark report, so that accuracy and recall metrics are demonstrated. | High | M | B2.3, B4.2 | Published report showcasing hybrid model precision/recall improvements on Soroban dataset. |
| **B4.4** | As a founder, I want to submit the Stellar Community Fund (SCF) Build Award interest form and community post, so that grant funding is secured. | High | M | B4.3 | Includes live demo link, benchmark data, open-source SDK repo, and partner testimonials. |
