"""
Unit and integration tests for API Key authentication.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_missing_header(client: AsyncClient):
    response = await client.post("/v1/analyze/contract", json={})
    assert response.status_code == 401
    assert "Missing Authorization Bearer header" in response.json()["detail"]


@pytest.mark.asyncio
async def test_auth_invalid_prefix(client: AsyncClient):
    headers = {"Authorization": "Bearer invalid_prefix_key_123"}
    response = await client.post("/v1/analyze/contract", json={}, headers=headers)
    assert response.status_code == 401
    assert "Invalid API key format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_auth_invalid_key(client: AsyncClient):
    headers = {"Authorization": "Bearer qig_live_nonexistentkey123456"}
    response = await client.post("/v1/analyze/contract", json={}, headers=headers)
    assert response.status_code == 401
    assert "Invalid or revoked API key" in response.json()["detail"]


@pytest.mark.asyncio
async def test_auth_valid_key(client: AsyncClient, seed_data: dict):
    live_key = seed_data["raw_live_key"]
    headers = {"Authorization": f"Bearer {live_key}"}
    response = await client.post("/v1/analyze/contract", json={}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert "risk_score" in data
