# Sprint Backlog — Stella Subdomain & Landing Page Integration

**Sprint:** Sprint Stella  
**Focus:** Subdomain setup (`stella.quantuminfra.io`), interactive landing page development, auth routing to QuantumInfra dashboard, API key & model enablement.  
**Goal:** Deliver a production-grade developer portal for QI Guard on Stellar with interactive scan demonstration and single-click onboarding into QuantumInfra.

---

## Committed User Stories

| Story ID | User Story | Priority | Status | Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **ST-1.1** | As a product manager, I want a PRD defining the Stella subdomain landing page specs, so that engineering has a clear blueprint. | High | Done | PRD written and archived at `docs/STELLA_LANDING_PAGE_PRD.md`. |
| **ST-1.2** | As a web dev, I want host-header detection for `stella.quantuminfra.io` and `/stella` fallback routes, so that users reach the custom landing page. | High | Done | Router detects `stella.` domain and mounts landing page. |
| **ST-1.3** | As a Soroban dev, I want an interactive live scan demo widget on the landing page, so that I can evaluate risk scoring before registering. | High | In Progress | Select contract templates, inspect classical vs. quantum scores, findings, resilience. |
| **ST-1.4** | As a site visitor, I want clear feature modules, quantum benchmark charts, and SDK tabs, so that I understand QI Guard's technical capabilities. | High | In Progress | Render Contract Risk, Behavioral Anomaly, Quantum Resilience, Quantum Benchmark, and SDK snippet tabs. |
| **ST-1.5** | As a developer, I want landing page CTAs to navigate seamlessly to `/auth?source=stella`, so that I am registered on QuantumInfra and sent to my dashboard. | High | In Progress | Auth page accepts `source=stella` and routes to `/dashboard/api-keys`. |
| **ST-1.6** | As an authenticated user, I want to generate `qig_live_` API keys and view `qi-guard-stellar-0.1.0` in my dashboard catalog, so that I can start querying endpoints. | High | In Progress | API Key generation functional and model catalog presents Stellar QI Guard models. |

---

## Definition of Done (DoD)

- [x] PRD created (`STELLA_LANDING_PAGE_PRD.md`)
- [ ] Subdomain router configured
- [ ] Stella Landing Page UI & Interactive Scan Widget built
- [ ] Auth routing linked to `/auth?source=stella`
- [ ] Dashboard API Key & Model Catalog updated
- [ ] Zero build/TypeScript compile errors (`npm run build`)
