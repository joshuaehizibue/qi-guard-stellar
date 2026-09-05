# QI-Guard for Stellar

> **Quantum-Enhanced Security Intelligence for Stellar / Soroban Smart Contracts**  
> Built for the Stellar Community Fund (SCF) Build Award.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688)](https://fastapi.tiangolo.com/)
[![PennyLane](https://img.shields.io/badge/PennyLane-0.35%2B-blueviolet)](https://pennylane.ai/)

---

## What is QI-Guard?

QI-Guard is a REST API + SDK suite that brings quantum-classical hybrid machine learning to Stellar blockchain security. It statically analyses Soroban WASM bytecode, detects on-chain behavioural anomalies, and scores post-quantum cryptographic readiness — all in a single API call.

---

## Architecture

```
Client (Python SDK / JS SDK / GitHub Action)
        │
        ▼  HTTPS / JSON
┌─────────────────────────────────────┐
│       FastAPI Gateway               │
│  Auth · Rate Limiting · OpenAPI     │
└───────────────┬─────────────────────┘
                │ Async Dispatch
                ▼
┌────────────────────────────────────────────────────────┐
│              Inference & Analysis Engine               │
│  ┌──────────────────┐  ┌────────────┐  ┌───────────┐  │
│  │ Contract Risk    │  │ Behavioral │  │ Quantum   │  │
│  │ WASM Disassembler│  │ Anomaly    │  │ Resilience│  │
│  └────────┬─────────┘  └─────┬──────┘  └─────┬─────┘  │
│           └──────────────────┼────────────────┘        │
│                              ▼                         │
│        ┌─────────────────────────────────────────┐     │
│        │  Quantum-Classical Hybrid Engine         │     │
│        │  PyTorch MLP + PennyLane PQC Circuit     │     │
│        └─────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────┘
                │
                ▼
  PostgreSQL · Redis · AWS S3 (model weights / WASM artifacts)
```

**Stack:** FastAPI · PyTorch · PennyLane · scikit-learn · SQLAlchemy · Redis · PostgreSQL · React (Vite) · Docker · AWS ECS

---

## Features

| Module | Description |
|---|---|
| **Contract Risk** | Static WASM disassembly — opcode frequency, CFG, `require_auth` path analysis |
| **Behavioral Anomaly** | Isolation forest over Stellar Horizon transaction streams |
| **Quantum Resilience** | Post-quantum cryptography surface scanner & readiness score |
| **Hybrid Engine** | Classical vs. quantum-circuit inference with Quantum Delta metrics |
| **Model Registry** | Immutable versioned model artifacts (SHA-256 hashed) in PostgreSQL + S3 |
| **Developer Dashboard** | React + Vite UI for live scan results and benchmark visualisation |
| **SDKs** | Python SDK & JavaScript SDK with CLI |
| **GitHub Action** | `quantuminfra/qi-guard-action` — drop-in CI gate for Soroban projects |

---

## Quickstart

### 1. Clone & Install

```bash
git clone https://github.com/joshuaehizibue/qi-guard-stellar.git
cd qi-guard-stellar

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Set DATABASE_URL, REDIS_URL, API keys, etc.
```

### 3. Run the API

```bash
uvicorn app.main:app --reload --port 8000
# Swagger UI → http://localhost:8000/docs
```

### 4. Run Tests

```bash
pytest
```

### 5. Run with Docker Compose

```bash
docker-compose up --build
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/v1/analyze/contract` | Analyse Soroban WASM binary or contract address |
| `POST` | `/v1/analyze/behavioral` | Ingest account transaction stream for anomaly scoring |
| `GET` | `/v1/resilience/{target}` | Post-quantum readiness score & cryptographic exposure |
| `GET` | `/v1/benchmarks/{job_id}` | Classical vs. hybrid precision / recall / F1 / latency |

Full spec available at `/docs` (Swagger) or `/redoc` (ReDoc) when running locally.

---

## GitHub Action

```yaml
# .github/workflows/security.yml
- name: QI-Guard Quantum Audit Gate
  uses: quantuminfra/qi-guard-action@v1
  with:
    api-key: ${{ secrets.QIGUARD_API_KEY }}
    wasm-path: "target/wasm32-unknown-unknown/release/my_contract.wasm"
    fail-severity: "HIGH"
    fail-score: 75
```

See [`actions/qi-guard-action/README.md`](actions/qi-guard-action/README.md) for full options.

---

## Project Structure

```
QIGuard/
├── app/                   # FastAPI application (API, services, models, schemas)
├── dashboard/             # React + Vite developer dashboard
├── sdks/
│   ├── python/            # Python SDK
│   └── js/                # JavaScript SDK + CLI
├── actions/
│   └── qi-guard-action/   # GitHub Action
├── deploy/aws/            # AWS ECS / infrastructure configs
├── tests/                 # Pytest test suite
├── docs/                  # Reports and supplementary docs
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Documentation

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — System design & ADRs
- [`API_CONTRACT.md`](API_CONTRACT.md) — Full API contract
- [`PRODUCT_BACKLOG.md`](PRODUCT_BACKLOG.md) — Feature backlog
- [`RISK_LOG.md`](RISK_LOG.md) — Risk register

---

## License

MIT © QI-Guard Contributors
