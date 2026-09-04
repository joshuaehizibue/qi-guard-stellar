"""
Sprint 4 End-to-End Integration Tests.
Validates:
- TSK-401: Deployment manifest files (Dockerfile, docker-compose, ECS task definition)
- TSK-402: Design partner onboarding, feedback, and telemetry aggregation
- TSK-403 & TSK-404: Scout comparative benchmark runner execution
- TSK-405: SCF Build Award documentation integrity
"""

import os
import pytest
from scripts.run_scout_comparison import run_benchmark


@pytest.mark.asyncio
async def test_partner_onboard_lifecycle(client):
    """Tests onboarding a new Soroban design partner and assigning Protocol tier."""
    req_body = {
        "organization_name": "Aquarius AMM",
        "contact_email": "security@aquarius.space",
        "protocol_category": "DEFI"
    }
    res = await client.post("/v1/partners/onboard", json=req_body)
    assert res.status_code == 200
    data = res.json()
    assert data["organization"] == "Aquarius AMM"
    assert data["tier"] == "PROTOCOL"
    assert "keys" in data
    assert data["keys"]["live_key"].startswith("qig_live_")
    assert data["keys"]["ci_key"].startswith("qig_ci_")


@pytest.mark.asyncio
async def test_partner_feedback_and_telemetry(client):
    """Tests recording developer feedback on findings and fetching aggregated telemetry."""
    # Submit feedback
    feedback_req = {
        "finding_id": "QIG-SCF-0041",
        "project_id": "prj_test_aquarius",
        "is_true_positive": True,
        "notes": "Verified missing require_auth() on transfer_admin()"
    }
    fb_res = await client.post("/v1/partners/feedback", json=feedback_req)
    assert fb_res.status_code == 200
    fb_data = fb_res.json()
    assert fb_data["finding_id"] == "QIG-SCF-0041"
    assert fb_data["is_true_positive"] is True

    # Retrieve aggregated telemetry
    tel_res = await client.get("/v1/partners/telemetry")
    assert tel_res.status_code == 200
    tel_data = tel_res.json()
    assert tel_data["active_design_partners"] >= 3
    assert "partner_roster" in tel_data
    assert float(tel_data["partner_reported_precision"].replace("%", "")) >= 90.0


def test_scout_comparison_script():
    """Runs the Scout vs. QI-Guard benchmark script and asserts recall boost."""
    results = run_benchmark()
    assert "scout" in results
    assert "hybrid" in results
    # Assert quantum hybrid model caught more vulnerabilities than static AST
    assert results["hybrid"]["recall"] > results["scout"]["recall"]
    assert results["hybrid"]["recall"] == 1.0


def test_deployment_artifacts_exist():
    """Validates that all Sprint 4 deployment manifests and documentation exist."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    assert os.path.exists(os.path.join(base_dir, "Dockerfile"))
    assert os.path.exists(os.path.join(base_dir, "docker-compose.yml"))
    assert os.path.exists(os.path.join(base_dir, "deploy/aws/ecs-task-definition.json"))
    assert os.path.exists(os.path.join(base_dir, "deploy/aws/cloudfront-spec.json"))
    assert os.path.exists(os.path.join(base_dir, ".github/workflows/deploy.yml"))
    assert os.path.exists(os.path.join(base_dir, "docs/benchmarks/QI_GUARD_VS_SCOUT_BENCHMARK_REPORT.md"))
    assert os.path.exists(os.path.join(base_dir, "docs/scf/SCF_BUILD_AWARD_APPLICATION.md"))
    assert os.path.exists(os.path.join(base_dir, "docs/scf/DEMO_WALKTHROUGH_SCRIPT.md"))
