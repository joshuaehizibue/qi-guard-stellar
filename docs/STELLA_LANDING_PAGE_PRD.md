# Product Requirements Document (PRD)
## QI Guard on Stella Subdomain & Landing Page (`stella.quantuminfra.io`)

**Version:** 1.0  
**Date:** September 2026  
**Status:** Approved for Engineering  
**Subdomain:** `stella.quantuminfra.io`  
**Target Chain:** Stellar / Soroban Smart Contracts  
**Target Audience:** Soroban smart contract developers, Stellar DeFi protocol teams, security auditors, SCF applicants  

---

## 1. Executive Summary & Vision

`stella.quantuminfra.io` serves as the dedicated portal for **QI-Guard — Stellar Edition**, QuantumInfra's quantum-enhanced security intelligence layer purpose-built for the Soroban smart-contract ecosystem.

The landing page communicates QI Guard's core value proposition:
> **"Continuous on-chain behavioral intelligence, Soroban WASM vulnerability detection, and post-quantum resilience scoring — delivered through a single API key in under 5 minutes."**

The landing page bridges public interest, developer conversion, interactive real-time demonstration, and single-click authentication into the primary QuantumInfra dashboard.

---

## 2. Goals & Key Performance Indicators (KPIs)

1. **Subdomain Independence:** Provide a tailored product landing page on `stella.quantuminfra.io` with dedicated Soroban ecosystem branding and messaging.
2. **Developer Conversion:** Drive sign-ups and API key generations by linking seamless auth routes (`/auth?source=stella`) to the standard QuantumInfra dashboard.
3. **Interactive Proof-of-Value:** Offer a zero-friction live scan widget on the page where developers can test sample Soroban WASM contracts or Stellar wallet addresses.
4. **Quantum Moat Demonstration:** Clearly highlight side-by-side classical vs. hybrid quantum benchmark metrics to prove quantum accuracy gains (+14% precision, +18% recall).

---

## 3. Information Architecture & Page Structure

```
[ Navigation Bar ] -> Logo, Product Modules, Quantum Benchmark, SDK Docs, Pricing, [ Sign In ] [ Get API Key ]
        │
[ Hero Section ] -> Headline, Subtitle, Badges (SCF / Soroban), CTAs ("Start Free", "Live Interactive Demo")
        │
[ Live Scan Widget ] -> Interactive contract bytecode & address scanner with real-time risk output
        │
[ Core Modules ] -> 4 Product Cards: Contract Risk API, Behavioral Anomaly Engine, Quantum Resilience, Quantum Benchmark
        │
[ Quantum Benchmark Visualizer ] -> Side-by-side Classical vs. Hybrid ML performance metrics chart & table
        │
[ Developer SDK Quickstart ] -> Code tabs: npm (@quantuminfra/qi-guard), Python (qi-guard), cURL, GitHub Actions CI/CD
        │
[ Ecosystem Integration & Trust ] -> Soroban ecosystem compatibility (Scout, Certora, OpenZeppelin, Stellar RPC)
        │
[ Pricing Tiers ] -> Developer (Free / 50 req), Builder ($49/mo / 500 req), Protocol ($199/mo / Unlimited)
        │
[ Auth Redirect CTA ] -> High-impact banner connecting directly to QuantumInfra Dashboard & Key Generator
        │
[ Footer ] -> Legal, Docs, GitHub, QuantumInfra Ecosystem Links
```

---

## 4. Feature Specifications

### 4.1 Subdomain Routing (`stella.quantuminfra.io`)
- Hostname matching rule detects `stella.quantuminfra.io` or `stella.*` host header and renders the Stella landing page at root `/`.
- Preview routes `/stella` and `/stella-guard` enabled for local development.

### 4.2 Interactive WASM & Address Scan Widget
- Allows users to select from pre-populated Soroban smart contract templates (e.g. `Soroban Token Vault`, `Liquidity Pool Router`, `DeFi Lending Protocol`) or paste WASM hex / Stellar account address (`G...`).
- Renders real-time analysis results:
  - Base Classical Risk Score vs. Hybrid Quantum Enhanced Score.
  - Severity Level (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
  - Specific Findings (e.g., `UNRESTRICTED_ADMIN_TRANSFER`, `MISSING_REQUIRE_AUTH`, `ED25519_KEY_EXPOSURE`).
  - Quantum Resilience Rating (`READY`, `PARTIALLY_READY`, `VULNERABLE`).

### 4.3 Side-by-Side Quantum Benchmark Visualizer
- Displays interactive comparison metrics:
  - **Precision:** Classical 78.4% vs. Hybrid Quantum 92.1% (+13.7%)
  - **Recall:** Classical 71.2% vs. Hybrid Quantum 89.5% (+18.3%)
  - **F1 Score:** Classical 0.746 vs. Hybrid Quantum 0.908 (+0.162)
  - **Latency:** Classical 42ms vs. Hybrid Quantum 54ms (transparent compute overhead)

### 4.4 Authentication & Dashboard Gateway
- CTAs ("Get API Key", "Sign Up", "Sign In") pass `redirect=/dashboard` and `source=stella`.
- Upon auth completion in `Auth.tsx`, users are redirected to `/dashboard/api-keys` with 1,000 complimentary API credits and pre-provisioned access to the `qi-guard-stellar-0.1.0` model.

---

## 5. Visual Design System

- **Color Palette:**
  - Background: Deep Slate Dark `#0A0E17` / `#111827`
  - Accent Gradients: Stellar Purple (`#7D00FF`) to Quantum Cyan (`#00F2FE`)
  - Status Indicators: Emerald `#10B981` (Pass/Low Risk), Amber `#F59E0B` (Medium), Rose `#EF4444` (Critical)
- **Typography:** Inter / System Sans-serif, crisp monospace font for code blocks (`JetBrains Mono` / `Fira Code`).
- **Effects:** Backdrop glassmorphic cards (`bg-slate-900/60 backdrop-blur-md border border-slate-800`), glowing subtle neon drop-shadows.

---

## 6. Definition of Done (DoD)

1. PRD completed and archived in documentation repository.
2. Subdomain routing functional on `stella.quantuminfra.io` and `/stella`.
3. Landing page fully built with responsive layout and interactive demo scanner widget.
4. Auth buttons linked to standard Quantum Infra dashboard sign-up flow (`/auth?source=stella`).
5. Authenticated users can generate API keys (`qig_live_...`) and access `qi-guard-stellar-0.1.0` in the dashboard.
6. TypeScript build passes with zero errors (`npm run build`).
