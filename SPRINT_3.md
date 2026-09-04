# Sprint 3 Backlog — QI-Guard for Stellar MVP

**Goal:** Build Phase 2 Developer Experience Suite — JS/TS SDK (`@quantuminfra/qi-guard`), Python SDK (`qi-guard`), GitHub Action (`quantuminfra/qi-guard-action`), and React Developer Dashboard.  
**Timebox:** 2 Weeks (Weeks 5–6)  
**Pulled from:** [`PRODUCT_BACKLOG.md`](file:///home/kami/Desktop/codebase/QIGuard/PRODUCT_BACKLOG.md) items `B3.3`, `B3.4`, `B3.5`, `B3.6`, `B3.7`.

---

## 1. Committed Sprint Tasks

| Task ID | Description | Source Story | Est. | Depends on | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TSK-301** | Build TypeScript/JavaScript SDK (`@quantuminfra/qi-guard`) with full type definitions, HTTP client, and `npx qi-guard` CLI binary. | `B3.3` | M | Phase 0/1 API | Completed |
| **TSK-302** | Build Python SDK (`qi-guard`) PyPI package with async/sync client wrapper and typed response dataclasses. | `B3.4` | M | Phase 0/1 API | Completed |
| **TSK-303** | Build GitHub Action (`quantuminfra/qi-guard-action`) with `action.yml` to run automated WASM risk checks on PRs and set CI check status. | `B3.5` | M | TSK-301 | Completed |
| **TSK-304** | Build React Developer Dashboard SPA with Project Management, API Key generation, Risk Findings table, and Quantum Benchmark charts. | `B3.6` | L | Phase 0/1 API | Completed |
| **TSK-305** | Integrate Stripe Billing & Webhook Handler for tier management (`Developer`, `Builder`, `Protocol`). | `B3.7` | M | Phase 0 Database | Completed |
| **TSK-306** | Write E2E integration test suite for JS SDK, Python SDK, GitHub Action simulator, and React Dashboard API router. | `B3.3`-`B3.7` | S | TSK-301-305 | Completed |

---

## 2. Sprint Acceptance Criteria & DoD Verification

This sprint satisfies all quality bar standards defined in [`DEFINITION_OF_DONE.md`](file:///home/kami/Desktop/codebase/QIGuard/DEFINITION_OF_DONE.md):

1. **JS/TS SDK Quickstart:** Developer can initialize `@quantuminfra/qi-guard` and query contract analysis in < 5 lines of code. (Verified: `sdks/js/dist/index.js` & `sdks/js/test/test_sdk.js`).
2. **CLI Command:** `npx qi-guard analyze --wasm ./my_contract.wasm` outputs formatted JSON / ASCII risk profile directly in terminal. (Verified: `sdks/js/bin/qi-guard.js`).
3. **GitHub Action Gate:** Action fails build pipeline when contract risk score exceeds `HIGH` threshold. (Verified: `actions/qi-guard-action/index.js` & `tests/test_sprint3_e2e.py`).
4. **React Dashboard:** Renders interactive side-by-side classical vs. hybrid metric charts and copyable API key management cards. (Verified: `dashboard/dist` production build).
5. **Stripe Billing:** Quota provisioning and upgrade webhook handler tested with 100% pass rate. (Verified: `tests/test_sprint3_e2e.py`).

