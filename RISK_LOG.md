# Risk & Assumptions Register — QI-Guard for Stellar MVP

**Last Updated:** August 2026  
**Status:** Active Tracking

---

## 1. Risk Matrix Overview

| Risk ID | Category | Severity | Probability | Risk Summary | Mitigation Strategy | Owner |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSK-01** | Technical | **High** | High | PennyLane CPU quantum circuit simulation latency overhead during API requests | Implement Redis-based asynchronous task queuing (ARQ/Celery) and cache feature embeddings | Lead ML Eng |
| **RSK-02** | Data | **High** | Medium | Sparse public dataset for Soroban Rust/WASM vulnerabilities | Augment dataset with synthetic WASM mutation samples and EVMbench-translated smart contract vectors | Data Lead |
| **RSK-03** | Infra | **Medium** | High | Horizon API & Soroban RPC rate limiting during deep ledger ingestion | Deploy local Horizon/RPC caching proxy with cursor-based chunking and backoff | Backend Lead |
| **RSK-04** | Market | **Medium** | Medium | User skepticism regarding quantum ML value proposition | Mandate side-by-side classical vs. hybrid benchmark metrics in every response to prove quantum delta | Product Lead |
| **RSK-05** | Schedule | **High** | Low | SCF Build Award submission deadline constraint (Week 16) | Timebox MVP features strictly to 4 core endpoints; defer multi-chain expansion to post-MVP | Project Lead |

---

## 2. Detailed Risk Analyses & Mitigation Plans

### RSK-01: PennyLane Quantum Circuit Simulation Bottlenecks
- **Impact:** High computational latency on PennyLane parameterized quantum circuits could cause API HTTP timeouts (> 5 seconds).
- **Mitigation:**
  1. Restrict qubit count in MVP variational circuit: `n_qubits = min(8, max(2, features))`.
  2. Use C++ lightning plugin state-vector simulator (`lightning.qubit`) for high-performance CPU execution.
  3. Pre-compute and cache classical feature embeddings in Redis.

### RSK-02: Sparse Soroban Vulnerability Dataset
- **Impact:** Model overfitting or poor generalization on real-world Soroban contracts due to young ecosystem history.
- **Mitigation:**
  1. Extract vulnerability taxonomy from historical Soroban audit reports (Soroban Security Portal / Inferara).
  2. Implement automated AST/bytecode mutation generator to produce synthetic bug variants.
  3. Map EVM security benchmark vectors into WASM control-flow equivalent features.

### RSK-03: Horizon RPC Ingestion Rate Limits
- **Impact:** Horizon API HTTP 429 errors when fetching multi-month ledger interaction histories for high-activity addresses.
- **Mitigation:**
  1. Enforce max 7-day default window for real-time `/analyze/behavioral` queries.
  2. Implement Redis caching with 1-hour TTL on computed address feature graphs.
  3. Provide batch endpoint capability for off-peak async batch ingestion.

---

## 3. Assumptions Register

| Assumption ID | Statement | Verification Method | Status |
| :--- | :--- | :--- | :--- |
| **ASM-01** | Soroban developers prefer a clean REST API / SDK over complex self-hosted CLI scanners. | Design partner interviews with 10 Soroban protocol teams in Phase 3. | Validated |
| **ASM-02** | Quantum circuit feature transformations provide measurable F1-score improvement on high-dimensional transaction graphs. | Continuous benchmarking during Phase 1 model training. | In Progress |
| **ASM-03** | Ed25519 public key exposure on Stellar ledgers is sufficient to calculate Quantum Resilience risk. | Audit of Stellar Horizon public ledger transaction payloads. | Validated |
