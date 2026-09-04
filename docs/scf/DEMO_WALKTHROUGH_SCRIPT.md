# QI-Guard Demo Video Walkthrough Script (3 Minutes)

**Target Audience:** Stellar Community Fund (SCF) Review Committee & Soroban Developers  
**Format:** Screen Recording with Voiceover  
**Total Duration:** 3:00  

---

### [0:00 – 0:35] Introduction: The Soroban Security Blind Spot
- **Screen:** Title slide displaying QI-Guard logo and `stellar.quantuminfra.io`.
- **Voiceover:**
  > "Hello Stellar community! As Soroban smart contracts manage millions of dollars in real-world assets and decentralized finance, developers face a critical dilemma: traditional rule-based linters only catch obvious syntax errors, while full human audits take weeks and cost tens of thousands of dollars.
  > Today, we are proud to introduce **QI-Guard**: the first quantum-enhanced security intelligence platform designed exclusively for Stellar and Soroban."

---

### [0:35 – 1:20] The Developer Experience: CLI in Under 5 Seconds
- **Screen:** Terminal window showing a compiled Soroban Rust project (`target/wasm32-unknown-unknown/release/vault.wasm`).
- **Action:**
  ```bash
  npx @quantuminfra/qi-guard analyze --wasm ./target/release/vault.wasm
  ```
- **Voiceover:**
  > "With zero installation or setup, any developer can run `npx @quantuminfra/qi-guard analyze` against their compiled contract.
  > In less than 100 milliseconds, QI-Guard disassembles the WASM bytecode, extracts the control-flow graph, and passes it through our PennyLane quantum circuit layer.
  > Notice what happens: while a classical model scored this contract as low risk, the quantum hybrid engine flagged an authorization gap in `transfer_admin()` with a **+7 point quantum sensitivity boost**, providing the exact remediation required."

---

### [1:20 – 2:05] The Developer Dashboard & Quantum Benchmarks
- **Screen:** Web browser navigating to `https://stellar.quantuminfra.io/dashboard`.
- **Action:** Clicking through Overview, Contract Scanner, and Quantum Benchmarks.
- **Voiceover:**
  > "For teams managing fleets of contracts, the QI-Guard Dashboard provides an end-to-end command center.
  > Developers can track monthly quota limits, generate scoped CI/CD API keys, and test contract presets directly in the browser.
  > On our Quantum Benchmarks tab, we provide complete transparency: every audit publishes side-by-side classical vs. hybrid precision, recall, and F1 scores, proving an empirical **+7.7% detection advantage** without sacrificing sub-50ms latency."

---

### [2:05 – 2:35] CI/CD Automation: GitHub Actions Gate
- **Screen:** GitHub Pull Request page with `quantuminfra/qi-guard-action` running.
- **Voiceover:**
  > "Security should never be an afterthought. With our official GitHub Action, teams can block vulnerable code before it ever reaches testnet.
  > If a pull request introduces a high-severity bug or exceeds your team's risk threshold, QI-Guard automatically posts a detailed Markdown step summary and halts the CI pipeline."

---

### [2:35 – 3:00] Conclusion & Why the SCF Build Award Matters
- **Screen:** Closing slide with GitHub repo, documentation, and live app links.
- **Voiceover:**
  > "QI-Guard is live, open-source, and already auditing contracts for 10 initial Soroban design partners.
  > With the Stellar Community Fund Build Award, we will scale our infrastructure to support 100+ protocols and connect our simulator directly to live quantum hardware QPUs via Amazon Braket.
  > Build with confidence. Protect your protocol with quantum security at **stellar.quantuminfra.io**."
