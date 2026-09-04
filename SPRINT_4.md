# Sprint 4 Backlog — QI-Guard for Stellar MVP

**Goal:** Deliver Phase 3 Ecosystem Integration & SCF Launch — AWS production deployment at `stellar.quantuminfra.io`, 10 Soroban design partner on-boarding telemetry, published "QI-Guard vs. Scout" comparative benchmark whitepaper, and SCF Build Award submission package.  
**Timebox:** 2 Weeks (Weeks 7–8)  
**Pulled from:** [`PRODUCT_BACKLOG.md`](file:///home/kami/Desktop/codebase/QIGuard/PRODUCT_BACKLOG.md) items `B4.1`, `B4.2`, `B4.3`, `B4.4`.

---

## 1. Committed Sprint Tasks

| Task ID | Description | Source Story | Est. | Depends on | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TSK-401** | Prepare Docker containerization, AWS ECS task definitions, RDS Postgres deployment manifests, and CloudFront SSL CDN routing for `stellar.quantuminfra.io`. | `B4.1` | M | Phase 2 Dashboard & API | Ready |
| **TSK-402** | Implement Design Partner Telemetry module with complimentary Protocol tier auto-provisioning and usage analytics instrumentation. | `B4.2` | M | Phase 2 Billing & DB | Ready |
| **TSK-403** | Run exhaustive comparative benchmark suite on shared Soroban vulnerability dataset: measure precision, recall, F1, and false-positive deltas between QI-Guard (hybrid) and Scout (static). | `B4.3` | L | Phase 1 Benchmark Engine | Ready |
| **TSK-404** | Author and publish Markdown/PDF "QI-Guard vs. Scout" Benchmark Whitepaper with reproducible dataset seeds and ROC curve plots. | `B4.3` | M | TSK-403 | Ready |
| **TSK-405** | Assemble Stellar Community Fund (SCF) Build Award submission package: project overview, working demo video, SDK documentation links, and partner testimonial quotes. | `B4.4` | M | TSK-401-404 | Ready |
| **TSK-406** | Conduct end-to-end production readiness verification, load testing (50 concurrent WASM scans), and release tag `v0.1.0-mvp`. | `B4.1`-`B4.4` | S | TSK-401-405 | Ready |

---

## 2. Sprint Acceptance Criteria & DoD

This sprint will be considered complete when all committed tasks meet the standards defined in [`DEFINITION_OF_DONE.md`](file:///home/kami/Desktop/codebase/QIGuard/DEFINITION_OF_DONE.md):

1. **Production Availability:** Live API responding at `stellar.quantuminfra.io/v1/health` with < 200ms latency.
2. **Benchmark Whitepaper:** Publicly accessible benchmark report detailing F1/recall gains (+7.7%) on Soroban test contracts over pure classical static rules.
3. **SCF Submission:** Complete grant application submitted to Stellar Community Fund Discord and portal.
4. **Partner Telemetry:** First 10 partner organizations active on complimentary Protocol tier with telemetry logged.
