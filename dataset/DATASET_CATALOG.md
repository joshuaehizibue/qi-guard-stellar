# Soroban Security Portal ML Training Dataset Catalog

**Corpus Version:** `1.0.0`  
**Dataset Name:** `soroban-security-portal-ml-corpus`  
**Primary Source:** [Inferara/soroban-security-portal](https://github.com/Inferara/soroban-security-portal) / [Stellar Security Portal](https://stellarsecurityportal.com)  
**Total Samples:** `121` (`96` Train / `25` Validation)  
**Positive / Vulnerable Ratio:** `47.9%`  
**Qubit Compatibility:** `8 Qubits` (8-dimensional base feature space)

---

## 1. Vulnerability Classes Extracted From Real Audits

| ID | Finding Title | Category | Severity | Protocol / Target | Upstream Commit References |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SSP-001** | Dispute resolver and platform can call with a... | `ACCESS_CONTROL_OR_AUTH` | **HIGH** | Trustless Work Smart Escrow | `main` |
| **SSP-002** | Maximum relative amount of fees not checked a... | `FEE_ARITHMETIC_OVERFLOW` | **HIGH** | Trustless Work Smart Escrow | `1da344e` |
| **SSP-003** | Initialization possible with pre-approved mil... | `INITIALIZATION_OR_STATE_BYPASS` | **MEDIUM** | Trustless Work Smart Escrow | `6d979b5` |
| **SSP-004** | Bypass of the Escrow Initialization Validatio... | `INITIALIZATION_OR_STATE_BYPASS` | **HIGH** | Trustless Work Smart Escrow | `main` |
| **SSP-005** | Front-running attack by a malicious platform ... | `INITIALIZATION_OR_STATE_BYPASS` | **HIGH** | Trustless Work Smart Escrow | `6d979b5` |
| **SSP-006** | Smart Escrow uses signed integer type i128 wi... | `FEE_ARITHMETIC_OVERFLOW` | **HIGH** | Trustless Work Smart Escrow | `6d979b5` |
| **SSP-007** | The Approver Can Disapprove Milestones... | `ACCESS_CONTROL_OR_AUTH` | **LOW** | Trustless Work Smart Escrow | `fe2623f` |
| **SSP-008** | Exceeding Assets Will Be Permanently Locked i... | `ASSET_LOCK_INVARIANT_VIOLATION` | **HIGH** | Trustless Work Smart Escrow | `2f6ef92` |
| **SSP-009** | Milestones can both be released and dispute-r... | `ASSET_LOCK_INVARIANT_VIOLATION` | **MEDIUM** | Trustless Work Smart Escrow | `bbdfcc4` |
| **SSP-010** | Gas optimizations... | `ACCESS_CONTROL_OR_AUTH` | **INFORMATIVE** | Trustless Work Smart Escrow | `4ee04c2`, `bba602a` |
| **SSP-011** | Initialization possible with zero milestones... | `FEE_ARITHMETIC_OVERFLOW` | **INFORMATIVE** | Trustless Work Smart Escrow | `ecbe0be` |
| **SSP-012** | At initialization, the decimals attribute of ... | `ACCESS_CONTROL_OR_AUTH` | **LOW** | Trustless Work Smart Escrow | `c76c7dd` |
| **SSP-013** | validate_release_conditions returns wrong err... | `LOGIC_VALIDATION_ERROR` | **INFORMATIVE** | Trustless Work Smart Escrow | `d77d7ae` |
| **SSP-014** | validate_release_conditions does not check wh... | `LOGIC_VALIDATION_ERROR` | **INFORMATIVE** | Trustless Work Smart Escrow | `5b9344f` |
| **SSP-015** | dispute_resolver should consent to Smart Escr... | `ACCESS_CONTROL_OR_AUTH` | **LOW** | Trustless Work Smart Escrow | `main` |
| **SSP-016** | Smart Escrows Are Deployers Despite Having Co... | `INITIALIZATION_OR_STATE_BYPASS` | **INFORMATIVE** | Trustless Work Smart Escrow | `main` |
| **SSP-017** | Disputed Funds Don't Go Back to Funders... | `LOGIC_VALIDATION_ERROR` | **MEDIUM** | Trustless Work Smart Escrow | `main` |
| **SSP-018** | The Trustless Work Platform Does Not Handle S... | `LOGIC_VALIDATION_ERROR` | **INFORMATIVE** | Trustless Work Smart Escrow | `main` |
| **SSP-019** | The Milestone Updates Phase Can Be Skipped... | `ASSET_LOCK_INVARIANT_VIOLATION` | **INFORMATIVE** | Trustless Work Smart Escrow | `93c4c37` |
| **SSP-020** | It Is Possible To Change The Platform Address... | `ACCESS_CONTROL_OR_AUTH` | **INFORMATIVE** | Trustless Work Smart Escrow | `118a316` |
| **SSP-021** | Differences Between the Single and Multi-Rele... | `ASSET_LOCK_INVARIANT_VIOLATION` | **INFORMATIVE** | Trustless Work Smart Escrow | `699e25e` |
| **SSP-022** | In-Memory Queue Storage Causing Data Loss and... | `LOGIC_VALIDATION_ERROR` | **HIGH** | Trustless Work Smart Escrow | `f353f3c` |
| **SSP-023** | Open CORS Policy Allowing Unauthorized Cross-... | `ACCESS_CONTROL_OR_AUTH` | **HIGH** | Trustless Work Smart Escrow | `4a82d73` |
| **SSP-024** | Missing Authentication Guards on Critical End... | `ACCESS_CONTROL_OR_AUTH` | **HIGH** | Trustless Work Smart Escrow | `4f7b37e` |
| **SSP-025** | Authorization Bypass in Escrow Repository... | `ACCESS_CONTROL_OR_AUTH` | **MEDIUM** | Trustless Work Smart Escrow | `f3ac8da` |
| **SSP-026** | Information Disclosure Through Error Messages... | `LOGIC_VALIDATION_ERROR` | **LOW** | Trustless Work Smart Escrow | `cb5d5f6` |
| **SSP-027** | HTTP Connections Allowed in Production Enviro... | `LOGIC_VALIDATION_ERROR` | **HIGH** | Trustless Work Smart Escrow | `6cc12b5` |
| **SSP-028** | Unsafe HTTP Methods for State-Changing Operat... | `LOGIC_VALIDATION_ERROR` | **HIGH** | Trustless Work Smart Escrow | `27c7ebe` |
| **SSP-029** | Type Safety Issues - From 'any' Types to Docu... | `INITIALIZATION_OR_STATE_BYPASS` | **INFORMATIVE** | Trustless Work Smart Escrow | `67c890c` |
| **SSP-030** | Incorrect Validation Decorators for Numeric F... | `FEE_ARITHMETIC_OVERFLOW` | **LOW** | Trustless Work Smart Escrow | `ee82a6e` |
| **SSP-031** | Client-Side Timestamps Creating Data Inconsis... | `LOGIC_VALIDATION_ERROR` | **LOW** | Trustless Work Smart Escrow | `7942bd4` |
| **SSP-032** | Missing Input Validation and Type Annotations... | `INTEGER_SIGNEDNESS_UNDERFLOW` | **HIGH** | Trustless Work Smart Escrow | `6667272` |
| **SSP-033** | Unreliable Type Guard Functions and Interface... | `FEE_ARITHMETIC_OVERFLOW` | **INFORMATIVE** | Trustless Work Smart Escrow | `3c84811` |
| **SSP-034** | Environment Configuration Management Issues... | `LOGIC_VALIDATION_ERROR` | **INFORMATIVE** | Trustless Work Smart Escrow | `702c7ed` |
| **SSP-035** | Code Quality and Documentation Issues... | `ACCESS_CONTROL_OR_AUTH` | **INFORMATIVE** | Trustless Work Smart Escrow | `c8e5a65` |
| **SSP-036** | Data Architecture and Repository Pattern Issu... | `INITIALIZATION_OR_STATE_BYPASS` | **INFORMATIVE** | Trustless Work Smart Escrow | `d005371` |
| **SSP-037** | Development Tooling and Code Quality Setup... | `LOGIC_VALIDATION_ERROR` | **INFORMATIVE** | Trustless Work Smart Escrow | `main` |
| **SSP-038** | Install ESLint and related packages... | `GRIEFING_STATE_REVERSION` | **MEDIUM** | Trustless Work Smart Escrow | `main` |
| **SSP-039** | Install Husky for git hooks... | `GRIEFING_STATE_REVERSION` | **MEDIUM** | Trustless Work Smart Escrow | `main` |
| **SSP-040** | Install Prettier and integration... | `GRIEFING_STATE_REVERSION` | **MEDIUM** | Trustless Work Smart Escrow | `main` |
| **SSP-041** | Install lint-staged for efficient pre-commit ... | `GRIEFING_STATE_REVERSION` | **MEDIUM** | Trustless Work Smart Escrow | `67c890c` |
| **SSP-042** | Backend allows for submitting any pre-signed ... | `ACCESS_CONTROL_OR_AUTH` | **LOW** | Trustless Work Smart Escrow | `9a4006e` |
| **SSP-043** | Singleton State Sharing in Transaction Builde... | `FEE_ARITHMETIC_OVERFLOW` | **MEDIUM** | Trustless Work Smart Escrow | `575a047` |
| **SSP-044** | Insecure private key storage in singleton ser... | `LOGIC_VALIDATION_ERROR` | **INFORMATIVE** | Trustless Work Smart Escrow | `939242c` |
| **SSP-045** | Inefficient database querying... | `LOGIC_VALIDATION_ERROR` | **LOW** | Trustless Work Smart Escrow | `5007e8d` |
| **SSP-046** | Notifications are created every hour once the... | `LOGIC_VALIDATION_ERROR` | **LOW** | Trustless Work Smart Escrow | `0652a79` |
| **SSP-047** | No notifications are being created for multi-... | `ASSET_LOCK_INVARIANT_VIOLATION` | **INFORMATIVE** | Trustless Work Smart Escrow | `ee38c9e` |
| **SSP-048** | Use of floating-point number type for critica... | `ACCESS_CONTROL_OR_AUTH` | **HIGH** | Trustless Work Smart Escrow | `ee82a6e` |
| **SSP-049** | API key does not meet security standards... | `ACCESS_CONTROL_OR_AUTH` | **HIGH** | Trustless Work Smart Escrow | `8360e9b` |
| **SSP-050** | Not using synced blockchain state in database... | `FRONT_RUNNING_RACE` | **INFORMATIVE** | Trustless Work Smart Escrow | `4298787` |
| **SSP-051** | API provided values are silently overridden w... | `LOGIC_VALIDATION_ERROR` | **INFORMATIVE** | Trustless Work Smart Escrow | `0843d1b` |
| **SSP-052** | Login authentication procedure does not authe... | `ACCESS_CONTROL_OR_AUTH` | **HIGH** | Trustless Work Smart Escrow | `8360e9b` |
| **SSP-053** | The backend relies on data in pendingWriteQue... | `FEE_ARITHMETIC_OVERFLOW` | **HIGH** | Trustless Work Smart Escrow | `main` |
| **SSP-054** | Missing validation whether user-submitted tra... | `LOGIC_VALIDATION_ERROR` | **HIGH** | Trustless Work Smart Escrow | `36ece55` |
| **SSP-055** | Recommendation: use self-hosted Stellar nodes... | `FEE_ARITHMETIC_OVERFLOW` | **INFORMATIVE** | Trustless Work Smart Escrow | `main` |
| **SSP-056** | set-trustline endpoint uses a private key as ... | `LOGIC_VALIDATION_ERROR` | **HIGH** | Trustless Work Smart Escrow | `939242c` |
| **SSP-057** | Issued JWT tokens never expire... | `ACCESS_CONTROL_OR_AUTH` | **LOW** | Trustless Work Smart Escrow | `8360e9b` |
| **SSP-058** | Potentially never-ending loop querying the St... | `LOGIC_VALIDATION_ERROR` | **HIGH** | Trustless Work Smart Escrow | `1b3bb0c` |

---

## 2. Feature Vector Specifications

### A. 8-Dimensional Base Features (`features_8d`)
*Directly mapped to PyTorch classical MLP encoder and PennyLane 8-qubit variational circuit (`n_qubits = 8`).*

| Index | Feature Dimension | Normalization Formula | Description |
| :---: | :--- | :--- | :--- |
| `[0]` | Byte Size | `min(1.0, byte_size / 5000.0)` | Normalized WASM bytecode binary size |
| `[1]` | Function Count | `min(1.0, fn_count / 50.0)` | Total declared & imported function count |
| `[2]` | Export Count | `min(1.0, export_count / 10.0)` | Number of exported contract entrypoints |
| `[3]` | Import Count | `min(1.0, import_count / 10.0)` | Host functions imported from `env` (e.g. `require_auth`) |
| `[4]` | Call Count | `min(1.0, call_count / 30.0)` | Internal & external call opcode frequency |
| `[5]` | Loop Density | `min(1.0, loop_count / 10.0)` | Unbounded loop instruction density |
| `[6]` | Finding Count | `min(1.0, findings / 5.0)` | Structural heuristic security findings |
| `[7]` | High Severity Flag | `1.0 if high else 0.0` | Binary indicator for critical authorization flaws |

### B. 16-Dimensional Extended Security Features (`features_16d`)
*Includes domain-specific Soroban contract semantics:*
- `[8]` Category ID normalized (`category_id / 10.0`)
- `[9]` Has authorization import check (`require_auth`)
- `[10]` Has signed `i128` without bound validations
- `[11]` State mutation indicator
- `[12]` Dynamic fee calculation logic (BPS overflow risk)
- `[13]` Unbounded loop / recursion indicator
- `[14]` Ground truth vulnerability label (`1.0` or `0.0`)
- `[15]` Structural complexity score

---

## 3. Data Split & File Layout

- **[`dataset/parsed/vulnerabilities.json`](parsed/vulnerabilities.json)**: Raw JSON structured audit records with code snippets and remediation instructions.
- **[`dataset/features/train_features.json`](features/train_features.json)**: 80% split for training classical PyTorch classifiers and optimizing PennyLane VQC parameters.
- **[`dataset/features/val_features.json`](features/val_features.json)**: 20% held-out test split for evaluating generalized precision, recall, and quantum delta.
- **[`dataset/features/metadata.json`](features/metadata.json)**: Hyperparameter and tensor configuration metadata.

---

## 4. How to Load and Train in Python

```python
import json
import torch

# Load training data
with open("dataset/features/train_features.json") as f:
    train_data = json.load(f)

# Extract 8-dim base features and binary labels
X_train = torch.tensor([item["features_8d"] for item in train_data], dtype=torch.float32)
y_train = torch.tensor([item["is_vulnerable"] for item in train_data], dtype=torch.float32).unsqueeze(1)

print(f"X_train shape: {X_train.shape}")  # (N, 8)
print(f"y_train shape: {y_train.shape}")  # (N, 1)

# Ready to pass to PyTorch MLP or PennyLane angle_embedding!
```
