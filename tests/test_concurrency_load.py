"""
Concurrency and Performance Load Test for QI-Guard FastAPI Backend.
Simulates 50 concurrent WASM analysis requests to verify sub-500ms p95 latency SLA.
"""

import asyncio
import time
import pytest
import httpx
from httpx import ASGITransport

from app.main import app
from app.core.database import get_db, Base
from app.core.security import generate_api_key
from app.models.project import Project, AccessTier
from app.models.api_key import APIKey, KeyType
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from conftest import test_engine, TestingSessionLocal


@pytest.mark.asyncio
async def test_concurrency_load_50_requests():
    """Executes 50 concurrent requests and verifies p95 latency stays under 500ms SLA."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed an active protocol project
    async with TestingSessionLocal() as session:
        project = Project(name="Load Test Protocol", tier=AccessTier.PROTOCOL)
        session.add(project)
        await session.flush()

        raw_key, prefix, key_hash = generate_api_key("live")
        api_key = APIKey(
            project_id=project.id,
            key_prefix=prefix,
            hashed_key=key_hash,
            key_type=KeyType.LIVE,
            name="Load Key"
        )
        session.add(api_key)
        await session.commit()

    async def _override_get_db():
        async with TestingSessionLocal() as s:
            yield s

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    latencies = []
    concurrency_count = 50

    async def send_single_analysis(client: httpx.AsyncClient, req_id: int):
        t0 = time.perf_counter()
        resp = await client.post(
            "/v1/analyze/contract",
            headers={"Authorization": f"Bearer {raw_key}"},
            json={
                "wasm_byte_code": "AGFzbQEAAAA=",
                "contract_address": f"CCW67TZJTGHVU2E5LILK2BEF2HCH66DY35ZJ3KBAE3B7D6AXDOJ{req_id:02d}",
                "network": "testnet"
            }
        )
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000)
        assert resp.status_code == 200, f"Request {req_id} failed with {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "job_id" in data
        assert "risk_score" in data

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        tasks = [send_single_analysis(client, i) for i in range(concurrency_count)]
        start_total = time.perf_counter()
        await asyncio.gather(*tasks)
        total_wall_time = (time.perf_counter() - start_total) * 1000

    app.dependency_overrides.clear()

    # Calculate latency distribution
    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.50)]
    p90 = latencies[int(len(latencies) * 0.90)]
    p95 = latencies[int(len(latencies) * 0.95)]
    max_lat = latencies[-1]

    print("\n" + "=" * 60)
    print("      CONCURRENCY LOAD TEST RESULTS (50 CONCURRENT REQUESTS)")
    print("=" * 60)
    print(f"Total Requests:      {concurrency_count}")
    print(f"Total Wall Clock:    {total_wall_time:.2f} ms")
    print(f"p50 Latency:         {p50:.2f} ms")
    print(f"p90 Latency:         {p90:.2f} ms")
    print(f"p95 Latency:         {p95:.2f} ms")
    print(f"Max Latency:         {max_lat:.2f} ms")
    print("=" * 60)

    # Verification of SLA (< 500ms p95)
    assert p95 < 500.0, f"p95 latency {p95:.2f}ms breached 500ms SLA!"


if __name__ == "__main__":
    asyncio.run(test_concurrency_load_50_requests())
