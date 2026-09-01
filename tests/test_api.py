"""
End-to-End API Integration Tests for all four QI-Guard endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_contract_analysis_endpoint(client: AsyncClient, seed_data: dict):
    headers = {"Authorization": f"Bearer {seed_data['raw_live_key']}"}
    payload = {
        "wasm_byte_code": "0x0061736d01000000010401600000020a0103656e76046175746800000713010e7472616e736665725f61646d696e00000a040102000b",
        "contract_address": "CCW67TZJTGHVU2E5LILK2BEF2HCH66DY35ZJ3KBAE3B7D6AXDOJ5",
        "network": "testnet"
    }
    response = await client.post("/v1/analyze/contract", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["job_id"].startswith("job_cnt_")
    assert data["severity"] == "HIGH"
    assert data["risk_score"]["classical"] > 0
    assert data["risk_score"]["hybrid"] >= data["risk_score"]["classical"]
    assert len(data["findings"]) > 0
    assert data["findings"][0]["id"] == "QIG-SCF-0041"


@pytest.mark.asyncio
async def test_behavioral_analysis_endpoint(client: AsyncClient, seed_data: dict):
    headers = {"Authorization": f"Bearer {seed_data['raw_live_key']}"}
    payload = {
        "address": "GABC123456789WXYZ123456789WXYZ123456789WXYZ",
        "analysis_window": "7d"
    }
    response = await client.post("/v1/analyze/behavioral", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["job_id"].startswith("job_beh_")
    assert "anomaly_score" in data
    assert len(data["patterns"]) > 0


@pytest.mark.asyncio
async def test_quantum_resilience_endpoint(client: AsyncClient, seed_data: dict):
    headers = {"Authorization": f"Bearer {seed_data['raw_live_key']}"}
    target = "GABC123456789WXYZ123456789WXYZ123456789WXYZ"
    response = await client.get(f"/v1/resilience/{target}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["target"] == target
    assert data["quantum_exposure_score"] == 61
    assert data["migration_status"] == "PARTIALLY_READY"


@pytest.mark.asyncio
async def test_quantum_benchmark_endpoint(client: AsyncClient, seed_data: dict):
    headers = {"Authorization": f"Bearer {seed_data['raw_live_key']}"}
    job_id = "job_cnt_8f9a2b1c"
    response = await client.get(f"/v1/benchmarks/{job_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["job_id"] == job_id
    assert "metrics" in data
    assert data["metrics"]["delta"]["quantum_contribution_positive"] is True
