#!/usr/bin/env python3
"""
QI-Guard Database Initializer & Seeder.
Initializes SQLAlchemy schema and seeds standard default projects, API keys,
contracts, and security findings for immediate local testing and production deployment.
"""

import os
import sys
import asyncio
import uuid
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import engine, Base, AsyncSessionLocal
from app.core.security import generate_api_key, hash_api_key
from app.models.project import Project, AccessTier
from app.models.api_key import APIKey, KeyType
from app.models.contract import Contract
from app.models.job import Job, JobType, JobStatus
from app.models.finding import Finding, Severity


DEFAULT_PROJECTS = [
    {
        "name": "Stellar Developer Sandbox",
        "tier": AccessTier.DEVELOPER,
        "live_key": "qig_live_dev_stellar_sandbox_2026",
        "test_key": "qig_test_dev_stellar_sandbox_2026",
        "desc": "Developer tier default project for local development & testing"
    },
    {
        "name": "Soroswap Protocol Labs",
        "tier": AccessTier.PROTOCOL,
        "live_key": "qig_live_soroswap_protocol_master_2026",
        "test_key": "qig_test_soroswap_protocol_master_2026",
        "desc": "Protocol tier partnership instance with unlimited contract audits"
    }
]


async def seed():
    print("=" * 70)
    print("      QI-GUARD FOR STELLAR: DATABASE INITIALIZER & SEEDER")
    print("=" * 70)

    # 1. Initialize Tables
    print("\n[1/3] Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("  => Schema tables verified: projects, contracts, api_keys, jobs, findings")

    # 2. Seed Projects & API Keys
    print("\n[2/3] Seeding default projects and API keys...")
    seeded_keys = []

    async with AsyncSessionLocal() as session:
        for p_data in DEFAULT_PROJECTS:
            # Check if project already exists
            res = await session.execute(select(Project).where(Project.name == p_data["name"]))
            existing = res.scalars().first()

            if not existing:
                project = Project(
                    id=str(uuid.uuid4()),
                    name=p_data["name"],
                    tier=p_data["tier"]
                )
                session.add(project)
                await session.flush()

                # Add Live Key
                live_raw = p_data["live_key"]
                live_prefix = live_raw[:12]
                live_hash = hash_api_key(live_raw)
                k_live = APIKey(
                    id=str(uuid.uuid4()),
                    project_id=project.id,
                    key_prefix=live_prefix,
                    hashed_key=live_hash,
                    key_type=KeyType.LIVE,
                    name="Master Live Key",
                    is_active=True
                )
                session.add(k_live)

                # Add Test Key
                test_raw = p_data["test_key"]
                test_prefix = test_raw[:12]
                test_hash = hash_api_key(test_raw)
                k_test = APIKey(
                    id=str(uuid.uuid4()),
                    project_id=project.id,
                    key_prefix=test_prefix,
                    hashed_key=test_hash,
                    key_type=KeyType.TEST,
                    name="Master Test Key",
                    is_active=True
                )
                session.add(k_test)

                seeded_keys.append({
                    "project": project.name,
                    "tier": project.tier.value,
                    "live_key": live_raw,
                    "test_key": test_raw
                })
            else:
                seeded_keys.append({
                    "project": existing.name,
                    "tier": existing.tier.value,
                    "live_key": p_data["live_key"],
                    "test_key": p_data["test_key"],
                    "note": "(already seeded)"
                })

        # 3. Seed Sample Contract & Finding
        print("\n[3/3] Seeding sample contract inspection records...")
        sample_contract_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        res = await session.execute(select(Contract).where(Contract.wasm_hash == sample_contract_hash))
        if not res.scalars().first():
            contract = Contract(
                id=str(uuid.uuid4()),
                contract_address="CCW67TZJTGHVU2E5LILK2BEF2HCH66DY35ZJ3KBAE3B7D6AXDOJ5",
                wasm_hash=sample_contract_hash,
                source_url="https://github.com/stellar/soroban-examples"
            )
            session.add(contract)
            await session.flush()

            # Retrieve first project
            res_p = await session.execute(select(Project))
            p0 = res_p.scalars().first()

            if p0:
                job = Job(
                    id=str(uuid.uuid4()),
                    project_id=p0.id,
                    contract_id=contract.id,
                    target_address=contract.contract_address,
                    job_type=JobType.CONTRACT_RISK,
                    status=JobStatus.COMPLETED,
                    classical_score=71.0,
                    hybrid_score=79.64,
                    delta_score=8.64,
                    classical_latency_ms=0.12,
                    hybrid_latency_ms=36.4,
                    model_version="qi-guard-stellar-0.1.0",
                    quantum_config={"n_qubits": 8, "circuit_depth": 4, "gate_set": ["RX", "RY", "CZ"]}
                )
                session.add(job)
                await session.flush()

                finding = Finding(
                    id=str(uuid.uuid4()),
                    job_id=job.id,
                    finding_code="QIG-SCF-0041",
                    finding_type="ACCESS_CONTROL",
                    component="transfer_admin()",
                    severity=Severity.HIGH,
                    evidence=["Exported function 'transfer_admin' contains state-mutating operations without invoking 'require_auth'."],
                    remediation="Inject soroban_sdk::Address::require_auth(&caller) at function entry point.",
                    quantum_contribution=True
                )
                session.add(finding)

        await session.commit()

    print("\n" + "=" * 70)
    print("      DATABASE INITIALIZATION COMPLETE")
    print("=" * 70)
    print(f"{'Project':<28} | {'Tier':<10} | {'Active Live Key'}")
    print("-" * 70)
    for k in seeded_keys:
        print(f"{k['project']:<28} | {k['tier']:<10} | {k['live_key']}")
    print("-" * 70)
    print("Use these keys in the Authorization Bearer header:")
    print("  curl -X POST http://localhost:8000/v1/analyze/contract \\")
    print(f"       -H 'Authorization: Bearer {seeded_keys[0]['live_key']}' \\")
    print("       -H 'Content-Type: application/json' ...\n")


if __name__ == "__main__":
    asyncio.run(seed())
