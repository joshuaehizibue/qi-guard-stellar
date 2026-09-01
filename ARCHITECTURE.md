# System Architecture & Decision Records — QI-Guard for Stellar MVP

**Version:** 1.0.0  
**Status:** Active / Engineering Baseline  
**Target Platform:** Stellar Blockchain / Soroban Smart Contracts  
**Hosting Environment:** AWS (ECS, RDS Postgres, ElastiCache Redis, S3)

---

## 1. High-Level System Architecture

QI-Guard provides a quantum-enhanced blockchain security intelligence layer delivered as a FastAPI REST backend and SDK suite.

```
                  ┌─────────────────────────────────────────┐
                  │     Developer / Client Application      │
                  │ (Python SDK / JS SDK / GitHub Action)   │
                  └────────────────────┬────────────────────┘
                                       │ HTTPS / JSON API
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │          FastAPI Gateway Layer          │
                  │   - API Key Auth (qig_live/test/ci)     │
                  │   - Rate Limiting & Tier Enforcement    │
                  │   - Request Router & OpenAPI Spec       │
                  └────────────────────┬────────────────────┘
                                       │ Async Dispatch
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            INFERENCE & ANALYSIS ENGINE                      │
│                                                                             │
│  ┌───────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐ │
│  │ Contract Risk Module  │  │ Behavioral Anomaly   │  │ Quantum Resilience│ │
│  │ - WASM Disassembler   │  │ - Horizon Streamer   │  │ - PQC Surface    │ │
│  │ - CFG & Feature Ext.  │  │ - Temporal Feature   │  │   Scanner        │ │
│  └───────────┬───────────┘  └───────────┬──────────┘  └────────┬─────────┘ │
│              │                          │                      │           │
│              └──────────────────────────┼──────────────────────┘           │
│                                         ▼                                  │
│                 ┌───────────────────────────────────────────┐              │
│                 │   Quantum-Classical Hybrid Engine         │              │
│                 │   - PyTorch Classical Encoder             │              │
│                 │   - PennyLane Variational Circuit Layer   │              │
│                 │   - Side-by-side Classical vs. Hybrid     │              │
│                 └─────────────────────┬─────────────────────┘              │
└───────────────────────────────────────┼────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER & MODEL REGISTRY                         │
│                                                                             │
│  ┌───────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐ │
│  │ PostgreSQL DB         │  │ Redis Cache & Queues │  │ Amazon S3        │ │
│  │ - Projects, Keys      │  │ - Task Queues        │  │ - Model Weights  │ │
│  │ - Findings & Reports  │  │ - Rate Limit Counters│  │ - WASM Artifacts │ │
│  └───────────────────────┘  └──────────────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Architecture Decisions (ADRs)

### ADR-001: Hybrid Quantum-Classical Pipeline Design
- **Context:** Classical ML models struggle with high-dimensional, sparse feature spaces typical of complex WASM bytecode and network flow graphs.
- **Decision:** Implement a two-path hybrid model. A PyTorch Multi-Layer Perceptron (MLP) encodes input features into a dense latent representation. This latent vector is fed into a PennyLane parameterized quantum circuit (PQC) using rotation gates (`n_qubits = min(8, max(2, features))`). Gradients are computed via the parameter-shift rule.
- **Consequence:** Every API inference runs both the pure classical head and the hybrid quantum head in parallel, measuring precise precision/recall/F1 deltas ("Quantum Delta").

### ADR-002: Soroban WASM Parser Architecture
- **Context:** Soroban smart contracts compile to WASM binary bytecode.
- **Decision:** Build a lightweight WASM parser using Rust bindings (`wasmparser` crate) with a Python C-extension interface (`pyo3`). Extract opcode frequency vectors, call graphs, import tables, and admin privilege management paths (`require_auth`).
- **Consequence:** Provides deterministic static analysis inputs to the feature engineering pipeline without requiring full execution sandboxing.

### ADR-003: Asynchronous Ingestion & Horizon/RPC Data Layer
- **Context:** Stellar ledger transaction history can be high-volume and subject to rate limits.
- **Decision:** Utilize FastAPI background tasks backed by Redis (Celery / ARQ) for asynchronous transaction fetching via Stellar Horizon REST API and Soroban RPC. Implement cursor-based pagination and local Redis caching for address interaction subgraphs (7-day window).
- **Consequence:** Prevents HTTP client timeouts on deep address audits while maintaining strict response time SLAs for cached data.

### ADR-004: Model Registry & Metadata Schema
- **Context:** Security models require auditability, version tracking, and reproducible benchmark history.
- **Decision:** Maintain an immutable Model Registry in PostgreSQL + S3. Every trained model artifacts bundle contains:
  - `model_id` (e.g., `qi-guard-stellar-0.1.0`)
  - `dataset_version` (SHA-256 hash of training corpus)
  - `quantum_config` (qubit count, circuit depth, gate set)
  - `model_hash` (SHA-256 of serialized weights)
- **Consequence:** Every risk finding returned to a client references the exact `model_id` and `quantum_contribution` boolean.

---

## 3. Data Flow & Security Model

### Authentication & Authorization Schema
API Keys follow a structured format scoped to project permissions:
- `qig_live_<hash>`: Production operational key (enforces rate limits by tier: Developer, Builder, Protocol).
- `qig_test_<hash>`: Testnet key (free tier sandbox).
- `qig_ci_<hash>`: Scoped strictly to contract WASM analysis (read-only project profile access, tailored for GitHub Actions).

---

## 4. Technology Stack Matrix

| Component | Choice | Justification |
| :--- | :--- | :--- |
| **API Framework** | FastAPI (Python 3.11) | Async support, fast JSON serialization, native OpenAPI spec generation. |
| **Quantum Framework** | PennyLane | Flexible hybrid PyTorch integration, automated parameter-shift differentiation. |
| **Classical ML** | PyTorch / scikit-learn | Efficient GPU/CPU tensor operations, isolation forest implementation. |
| **WASM Disassembler** | Rust `wasmparser` + `pyo3` | High-performance WASM parsing and control-flow graph construction. |
| **Database** | PostgreSQL 15 | Relational integrity for user accounts, API keys, findings, and benchmark logs. |
| **Cache & Queue** | Redis 7 | High-speed rate limiting, task queues, and graph feature caching. |
| **Storage** | AWS S3 | Storage of raw WASM binaries, model weight artifacts, and audit reports. |
