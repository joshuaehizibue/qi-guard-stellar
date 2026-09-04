# @quantuminfra/qi-guard

Official JavaScript and TypeScript SDK for **QI-Guard Quantum Smart Contract Security** on Stellar/Soroban.

## Installation

```bash
npm install @quantuminfra/qi-guard
```

## Quickstart (Node / TypeScript)

```typescript
import { QIGuardClient } from "@quantuminfra/qi-guard";

const client = new QIGuardClient({
  apiKey: process.env.QIGUARD_API_KEY
});

// Analyze a Soroban contract WASM binary
const report = await client.analyzeContract({
  wasm_byte_code: "AGFzbQEAAAA...",
  network: "testnet"
});

console.log(`Risk Score: ${report.risk_score.hybrid} (${report.severity})`);
console.log(`Quantum Delta Gain: +${report.risk_score.delta} pts`);
```

## CLI Usage (`npx qi-guard`)

```bash
# Analyze a compiled Soroban WASM contract
npx qi-guard analyze --wasm ./target/wasm32-unknown-unknown/release/my_contract.wasm

# Inspect NIST Post-Quantum Cryptography (PQC) readiness
npx qi-guard resilience CA3D5KRYM6CB7OWQ6TWYRR3TO4CGZMWCCQVDAITJN5...

# View side-by-side classical vs. quantum benchmark deltas
npx qi-guard benchmark job_cnt_8f9a2b1c
```
