# Sprint 2 Backlog — QI-Guard for Stellar MVP

**Goal:** Build Phase 1 Intelligence Engine — classical vulnerability classifier, PennyLane variational quantum circuit layer, Behavioral Isolation Forest anomaly engine, Quantum Resilience PQC scanner, and Model Registry.  
**Timebox:** 2 Weeks (Weeks 3–4)  
**Pulled from:** [`PRODUCT_BACKLOG.md`](file:///home/kami/Desktop/codebase/QIGuard/PRODUCT_BACKLOG.md) items `B2.1`, `B2.2`, `B2.3`, `B2.4`, `B2.5`, `B2.6`.

---

## 1. Committed Sprint Tasks

| Task ID | Description | Source Story | Est. | Depends on | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TSK-201** | Implement PyTorch MLP classical encoder & vulnerability classifier for WASM static opcode features. | `B2.1` | M | Phase 0 WASM Parser | Ready |
| **TSK-202** | Implement PennyLane variational quantum circuit layer (`n_qubits = min(8, max(2, features))`) with parameter-shift gradients. | `B2.2` | L | TSK-201 | Ready |
| **TSK-203** | Build Quantum Benchmark Engine to run classical and hybrid models in parallel and compute precision/recall/F1/latency deltas. | `B2.3` | M | TSK-202 | Ready |
| **TSK-204** | Implement Behavioral Anomaly Detection pipeline combining temporal Horizon feature engineering with Isolation Forests. | `B2.4` | M | Phase 0 Horizon Client | Ready |
| **TSK-205** | Implement Quantum Resilience PQC scanner mapping Ed25519/Secp256k1 key surfaces against NIST PQC migration criteria. | `B2.5` | S | Phase 0 Horizon Client | Ready |
| **TSK-206** | Build immutable Model Registry service with SHA-256 weight hashing, dataset versioning, and Postgres model metadata logging. | `B2.6` | M | TSK-203 | Ready |
| **TSK-207** | Integrate Intelligence Engine models into FastAPI endpoints (`POST /v1/analyze/contract`, `POST /v1/analyze/behavioral`). | `B2.1`-`B2.5` | M | TSK-203, TSK-204 | Ready |
| **TSK-208** | Expand test suite to verify hybrid quantum circuit execution, benchmark delta calculations, and model registry persistence. | `B2.1`-`B2.6` | S | TSK-207 | Ready |

---

## 2. Sprint Acceptance Criteria & DoD

This sprint will be considered complete when all committed tasks meet the standards defined in [`DEFINITION_OF_DONE.md`](file:///home/kami/Desktop/codebase/QIGuard/DEFINITION_OF_DONE.md):

1. **Hybrid Inference Pipeline:** PennyLane parameterized circuit executes on classical embeddings without convergence errors or state-vector numerical instability.
2. **Benchmark Delta Tracking:** Every API response includes positive or zero `f1_improvement` and latency delta.
3. **Model Registry Tracking:** Every model execution logs model ID `qi-guard-stellar-0.1.0` and SHA-256 weight hash to database.
4. **Automated Testing:** Pytest suite passes 100% of test cases including hybrid circuit simulations.
