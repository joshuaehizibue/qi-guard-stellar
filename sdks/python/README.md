# qi-guard (Python SDK)

Official Python SDK for **QI-Guard Quantum Smart Contract Security** on Stellar/Soroban.

## Installation

```bash
pip install qi-guard
```

## Usage

```python
from qi_guard import QIGuardClient

client = QIGuardClient(api_key="qig_live_...")

# Analyze compiled Soroban WASM contract
with open("vault.wasm", "rb") as f:
    report = client.analyze_contract(wasm_bytes=f.read())

print(f"Risk Score: {report.risk_score.hybrid} / Severity: {report.severity}")
print(f"Quantum Gain: +{report.risk_score.delta} points sensitivity")

for finding in report.findings:
    print(f"- [{finding.severity}] {finding.type}: {finding.remediation}")
```

### Async Client

```python
import asyncio
from qi_guard import AsyncQIGuardClient

async def main():
    async with AsyncQIGuardClient(api_key="qig_live_...") as client:
        report = await client.analyze_contract(wasm_byte_code="AGFzbQEAAAA...")
        print(report.risk_score)

asyncio.run(main())
```
