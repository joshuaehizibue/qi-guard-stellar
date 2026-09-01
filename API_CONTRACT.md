# API Interface Contract — QI-Guard for Stellar MVP

**Base URL:** `https://stellar.quantuminfra.io/v1`  
**Authentication:** HTTP Bearer Header (`Authorization: Bearer qig_live_xxx`)  
**Specification Standard:** OpenAPI 3.0.3

---

## 1. Endpoints Overview

| Method | Endpoint | Description | Scopes |
| :--- | :--- | :--- | :--- |
| `POST` | `/analyze/contract` | Submit Soroban WASM or Rust source for vulnerability analysis | `contract:analyze` |
| `POST` | `/analyze/behavioral` | Stream or submit Stellar address activity for anomaly detection | `behavior:analyze` |
| `GET` | `/resilience/{target}` | Retrieve post-quantum security readiness score for account/contract | `resilience:read` |
| `GET` | `/benchmarks/{job_id}` | Retrieve side-by-side classical vs. hybrid model metrics | `benchmark:read` |

---

## 2. Detailed API Specifications

### 2.1 POST `/analyze/contract`
Submits a Soroban WASM binary (or base64 encoded string) to analyze static vulnerability patterns, administrative risks, and hybrid quantum-classical risk scores.

#### Request Headers
```http
Authorization: Bearer qig_live_xxxxxxxxxxxxxxxxxxxx
Content-Type: application/json
```

#### Request Body
```json
{
  "wasm_byte_code": "AGFzbQEAAAA...",
  "contract_address": "CCW67TZJTGHVU2E5LILK2BEF2HCH66DY35ZJ3KBAE3B7D6AXDOJ5...",
  "source_code_url": "https://github.com/example/soroban-vault",
  "network": "mainnet"
}
```

#### Response Body (`200 OK`)
```json
{
  "job_id": "job_cnt_8f9a2b1c",
  "contract_id": "CCW67TZJTGHVU2E5LILK2BEF2HCH66DY35ZJ3KBAE3B7D6AXDOJ5",
  "risk_score": {
    "classical": 71,
    "hybrid": 78,
    "delta": 7
  },
  "severity": "HIGH",
  "confidence": 0.91,
  "findings": [
    {
      "id": "QIG-SCF-0041",
      "type": "ACCESS_CONTROL",
      "component": "transfer_admin()",
      "severity": "HIGH",
      "evidence": [
        "unrestricted caller",
        "missing require_auth() check"
      ],
      "remediation": "Add require_auth() on the invoker address prior to state mutation",
      "model_version": "qi-guard-stellar-0.1.0",
      "quantum_contribution": true
    }
  ],
  "quantum_resilience": {
    "score": 38,
    "status": "NOT_READY"
  },
  "timestamp": "2026-09-01T22:30:00Z"
}
```

---

### 2.2 POST `/analyze/behavioral`
Analyzes Stellar address interaction history for behavioral anomalies using temporal sequence engineering and variational quantum circuit feature transformation.

#### Request Body
```json
{
  "address": "GABC123456789WXYZ...",
  "analysis_window": "7d",
  "transactions": []
}
```

#### Response Body (`200 OK`)
```json
{
  "job_id": "job_beh_3d4e5f6a",
  "address": "GABC123456789WXYZ...",
  "analysis_window": "7d",
  "anomaly_score": {
    "classical": 0.73,
    "hybrid": 0.81,
    "delta": 0.08
  },
  "risk_level": "HIGH",
  "patterns": [
    {
      "type": "RAPID_DRAIN",
      "confidence": 0.88,
      "evidence": [
        "12 high-value payment ops in 4 minutes",
        "all recipient accounts created within 1 hour"
      ]
    },
    {
      "type": "UNUSUAL_INVOCATION",
      "confidence": 0.77,
      "evidence": [
        "non-standard invocation sequence on liquidity pool contract"
      ]
    }
  ],
  "related_addresses": [
    "GDEF456789012UVW...",
    "GHIJ789012345RST..."
  ],
  "model_version": "qi-guard-stellar-0.1.0",
  "timestamp": "2026-09-01T22:30:00Z"
}
```

---

### 2.3 GET `/resilience/{target}`
Retrieves a cryptographic surface and post-quantum migration readiness score for a target Stellar address or deployed Soroban contract.

#### Path Parameters
- `target`: Stellar account address (`G...`) or Soroban contract address (`C...`).

#### Response Body (`200 OK`)
```json
{
  "target": "GABC123456789WXYZ...",
  "quantum_exposure_score": 61,
  "migration_status": "PARTIALLY_READY",
  "findings": [
    {
      "type": "EXPOSED_PUBLIC_KEY",
      "severity": "HIGH",
      "detail": "Ed25519 public key exposed on 47 ledger transactions — targetable by Grover/Shor acceleration",
      "mitigation": "Establish key rotation policies and prepare for hybrid PQC signature wrappers"
    }
  ],
  "readiness_checklist": {
    "key_rotation_policy": false,
    "pqc_compatible_library": false,
    "crypto_agility": "partial"
  },
  "timestamp": "2026-09-01T22:30:00Z"
}
```

---

### 2.4 GET `/benchmarks/{job_id}`
Returns side-by-side performance metrics comparing pure classical inference against the hybrid quantum-classical pipeline.

#### Path Parameters
- `job_id`: Unique identifier returned from an `/analyze/*` call.

#### Response Body (`200 OK`)
```json
{
  "job_id": "job_cnt_8f9a2b1c",
  "model_version": "qi-guard-stellar-0.1.0",
  "quantum_config": {
    "n_qubits": 8,
    "circuit_depth": 4,
    "gate_set": ["RX", "RY", "CZ"]
  },
  "metrics": {
    "classical": {
      "precision": 0.84,
      "recall": 0.81,
      "f1_score": 0.825,
      "latency_ms": 42
    },
    "hybrid": {
      "precision": 0.91,
      "recall": 0.89,
      "f1_score": 0.900,
      "latency_ms": 118
    },
    "delta": {
      "f1_improvement": 0.075,
      "latency_cost_ms": 76,
      "quantum_contribution_positive": true
    }
  }
}
```

---

## 3. Standard Error Structure

All HTTP error responses adhere to standard RFC 7807 problem details:

```json
{
  "type": "https://stellar.quantuminfra.io/errors/RATE_LIMIT_EXCEEDED",
  "title": "Rate Limit Exceeded",
  "status": 429,
  "detail": "Developer tier monthly limit reached (50 contract analyses). Upgrade to Builder tier.",
  "instance": "/v1/analyze/contract"
}
```
