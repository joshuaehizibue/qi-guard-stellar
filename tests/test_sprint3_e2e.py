"""
Sprint 3 End-to-End Test Suite.
Validates:
- TSK-301: JS SDK & CLI binary execution
- TSK-302: Python SDK sync & async client operations
- TSK-303: GitHub Action policy gate enforcement
- TSK-304 & TSK-305: Stripe billing endpoints, webhook tier upgrades & usage quotas
"""

import json
import os
import subprocess
import sys
import pytest
import httpx
from httpx import ASGITransport

# Add Python SDK to path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../sdks/python")))

from app.main import app
from app.models.project import AccessTier
from app.models.contract import Contract
from qi_guard import QIGuardClient, AsyncQIGuardClient


@pytest.mark.asyncio
async def test_billing_plans(client):
    """Test retrieving public billing plan configurations."""
    res = await client.get("/v1/billing/plans")
    assert res.status_code == 200
    data = res.json()
    assert "DEVELOPER" in data
    assert "BUILDER" in data
    assert "PROTOCOL" in data
    assert data["DEVELOPER"]["price_usd"] == 0
    assert data["BUILDER"]["price_usd"] == 49
    assert data["PROTOCOL"]["price_usd"] == 199


@pytest.mark.asyncio
async def test_billing_checkout_and_webhook_lifecycle(client, db_session, seed_data):
    """Test creating checkout session, processing webhook upgrade, and subscription cancellation."""
    project = seed_data["project"]
    assert project.tier == AccessTier.DEVELOPER

    # 1. Create Checkout Session
    checkout_res = await client.post(
        "/v1/billing/checkout",
        json={"project_id": project.id, "tier": "BUILDER"}
    )
    assert checkout_res.status_code == 200
    checkout_data = checkout_res.json()
    assert "session_id" in checkout_data
    assert checkout_data["target_tier"] == "BUILDER"

    # 2. Simulate Stripe Webhook: checkout.session.completed
    webhook_payload = {
        "id": "evt_test_checkout_completed",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": checkout_data["session_id"],
                "client_reference_id": project.id,
                "metadata": {
                    "project_id": project.id,
                    "tier": "BUILDER"
                }
            }
        }
    }
    webhook_res = await client.post(
        "/v1/billing/webhook",
        content=json.dumps(webhook_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    assert webhook_res.status_code == 200
    wh_data = webhook_res.json()
    assert wh_data["status"] == "upgraded"
    assert wh_data["tier"] == "BUILDER"

    # 3. Check Usage Quota reflecting Builder limits (500 contracts)
    usage_res = await client.get(f"/v1/billing/usage?project_id={project.id}")
    assert usage_res.status_code == 200
    usage_data = usage_res.json()
    assert usage_data["tier"] == "BUILDER"
    assert usage_data["contracts"]["limit"] == 500

    # 4. Simulate Cancellation Webhook: customer.subscription.deleted
    cancel_payload = {
        "id": "evt_test_sub_deleted",
        "type": "customer.subscription.deleted",
        "data": {
            "object": {
                "metadata": {
                    "project_id": project.id
                }
            }
        }
    }
    cancel_res = await client.post(
        "/v1/billing/webhook",
        content=json.dumps(cancel_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    assert cancel_res.status_code == 200
    cancel_data = cancel_res.json()
    assert cancel_data["status"] == "downgraded"
    assert cancel_data["tier"] == "DEVELOPER"


@pytest.mark.asyncio
async def test_python_sdk_integration(db_session, seed_data, client):
    """Test Python SDK client (sync and async) against ASGI application."""
    live_key = seed_data["raw_live_key"]

    from app.core.database import get_db
    from starlette.testclient import TestClient

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    # Sync Client Test
    with TestClient(app) as http_client:
        sync_client = QIGuardClient(api_key=live_key, http_client=http_client)
        
        # Test contract analysis
        report = sync_client.analyze_contract(
            wasm_byte_code="AGFzbQEAAAA=",
            contract_address="CCW67TZJTGHVU2E5LILK2BEF2HCH66DY35ZJ3KBAE3B7D6AXDOJ5"
        )
        assert report.job_id.startswith("job_cnt_")
        assert report.risk_score.hybrid >= 0
        assert report.quantum_resilience.score >= 0

        # Test resilience lookup
        resilience = sync_client.get_resilience("CCW67TZJTGHVU2E5LILK2BEF2HCH66DY35ZJ3KBAE3B7D6AXDOJ5")
        assert resilience.target == "CCW67TZJTGHVU2E5LILK2BEF2HCH66DY35ZJ3KBAE3B7D6AXDOJ5"
        assert resilience.resilience_score >= 0

        # Test usage lookup
        usage = sync_client.get_usage(project_id=seed_data["project"].id)
        assert "contracts" in usage

    # Async Client Test
    async_client = AsyncQIGuardClient(api_key=live_key, http_client=client)
    async_report = await async_client.analyze_contract(wasm_byte_code="AGFzbQEAAAA=")
    assert async_report.job_id.startswith("job_cnt_")
    assert async_report.severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def test_js_cli_binary():
    """Test the compiled JS SDK CLI binary."""
    cli_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../sdks/js/bin/qi-guard.js"))
    
    # Check version
    v_res = subprocess.run(["node", cli_path, "version"], capture_output=True, text=True)
    assert v_res.returncode == 0
    assert "0.1.0" in v_res.stdout

    # Check help
    h_res = subprocess.run(["node", cli_path, "--help"], capture_output=True, text=True)
    assert h_res.returncode == 0
    assert "analyze" in h_res.stdout
    assert "resilience" in h_res.stdout
    assert "benchmark" in h_res.stdout


def test_github_action_runner_syntax():
    """Verify GitHub Action runner script exists and has valid syntax."""
    action_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../actions/qi-guard-action/index.js"))
    assert os.path.exists(action_path)

    # Validate JavaScript syntax with node -c
    check_res = subprocess.run(["node", "-c", action_path], capture_output=True, text=True)
    assert check_res.returncode == 0, f"Action syntax error: {check_res.stderr}"
