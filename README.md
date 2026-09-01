# QI-Guard for Stellar — MVP Edition

> **Quantum-Enhanced Security Intelligence Layer for Stellar / Soroban**  
> Technical documentation & implementation reference for the Stellar Community Fund (SCF) Build Award.

---

## Architecture & Features

- **FastAPI Core Gateway:** Async REST API serving contract risk, behavioral anomaly detection, quantum resilience scoring, and benchmark metrics.
- **WASM Disassembler:** Static feature extractor for Soroban WASM binaries (opcodes, control-flow graphs, host function imports, access control rule checks).
- **Quantum-Classical Hybrid Engine:** PyTorch classical MLP encoder + PennyLane parameterized variational quantum circuit with parameter-shift differentiation.
- **Stellar Data Layer:** Native Horizon REST API client & Soroban JSON-RPC client with exponential backoff retries.
- **API Key & Scope Auth:** Structured key hierarchy (`qig_live_`, `qig_test_`, `qig_ci_`) with tier-based rate limiting (Developer, Builder, Protocol).

---

## Quickstart

### 1. Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run API Gateway
```bash
uvicorn app.main:app --reload --port 8000
```
Open interactive Swagger docs at `http://localhost:8000/docs`.

### 3. Run Test Suite
```bash
pytest
```

---

## API Endpoints Summary

- `POST /v1/analyze/contract`: Submit Soroban WASM binary or contract address for static & hybrid vulnerability scoring.
- `POST /v1/analyze/behavioral`: Ingest Stellar account transaction streams to compute behavioral anomaly risk.
- `GET /v1/resilience/{target}`: Retrieve post-quantum readiness score & cryptographic exposure details.
- `GET /v1/benchmarks/{job_id}`: Inspect side-by-side classical vs. hybrid precision, recall, F1, and latency deltas.
