# quantuminfra/qi-guard-action

GitHub Action to automatically scan Soroban smart contracts on Stellar with **QI-Guard Quantum Security**.

## Workflow Example

Add this workflow to `.github/workflows/security.yml`:

```yaml
name: "Soroban Smart Contract Security Audit"

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  qi-guard-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Soroban Contract
        run: |
          cargo build --target wasm32-unknown-unknown --release

      - name: Run QI-Guard Quantum Audit Gate
        uses: quantuminfra/qi-guard-action@v1
        with:
          api-key: ${{ secrets.QIGUARD_API_KEY }}
          wasm-path: "target/wasm32-unknown-unknown/release/my_contract.wasm"
          fail-severity: "HIGH"
          fail-score: 75
```
