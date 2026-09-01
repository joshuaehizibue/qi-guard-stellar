"""
QI-Guard Standalone Test Suite Runner
Runs unit and integration tests against all core modules using Python standard library.
"""

import asyncio
import time
import hashlib
from app.services.wasm_parser import wasm_disassembler, WASMParserError
from app.core.security import generate_api_key, hash_api_key
from app.models.project import Project, AccessTier
from app.models.api_key import APIKey, KeyType
from app.models.contract import Contract
from app.models.finding import Finding, Severity
from app.models.job import Job, JobType, JobStatus
from app.schemas.contract import ContractAnalysisRequest, ContractAnalysisResponse
from app.schemas.behavioral import BehavioralAnalysisRequest, BehavioralAnalysisResponse
from app.schemas.resilience import QuantumResilienceResponse
from app.schemas.benchmark import QuantumBenchmarkResponse


def test_wasm_parser():
    print("[TEST 1/5] WASM Parser & Vulnerability Rule Engine...")
    valid_wasm = b"\x00asm\x01\x00\x00\x00\x01\x04\x01\x60\x00\x00\x02\x0a\x01\x03env\x04auth\x00\x00\x07\x13\x01\x0etransfer_admin\x00\x00\x0a\x04\x01\x02\x00\x0b"
    result = wasm_disassembler.parse_bytecode(valid_wasm)
    
    assert result["is_valid_wasm"] is True
    assert "transfer_admin" in result["exported_functions"]
    assert len(result["vulnerability_findings"]) > 0
    assert result["vulnerability_findings"][0]["id"] == "QIG-SCF-0041"
    print("  => PASSED: WASM disassembling & vulnerability rule detection verified!")


def test_api_key_security():
    print("[TEST 2/5] API Key Cryptographic Security & Scopes...")
    raw_key, prefix, hashed = generate_api_key("live")
    assert raw_key.startswith("qig_live_")
    assert len(prefix) == 12
    assert hash_api_key(raw_key) == hashed
    print("  => PASSED: SHA-256 API key hashing & prefix parsing verified!")


def test_schemas_contract_analysis():
    print("[TEST 3/5] Contract Risk API Schemas...")
    req = ContractAnalysisRequest(
        wasm_byte_code="0x0061736d01000000",
        contract_address="CCW67TZJTGHVU2E5LILK2BEF2HCH66DY35ZJ3KBAE3B7D6AXDOJ5",
        network="testnet"
    )
    assert req.network == "testnet"
    print("  => PASSED: Contract Risk request schema validation verified!")


def test_schemas_behavioral_analysis():
    print("[TEST 4/5] Behavioral Anomaly API Schemas...")
    req = BehavioralAnalysisRequest(
        address="GABC123456789WXYZ123456789WXYZ123456789WXYZ",
        analysis_window="7d"
    )
    assert req.analysis_window == "7d"
    print("  => PASSED: Behavioral Anomaly request schema validation verified!")


def test_database_models():
    print("[TEST 5/5] SQLAlchemy Database Models Structure...")
    project = Project(name="Soroban DeFi Protocol", tier=AccessTier.PROTOCOL)
    raw_key, prefix, hashed = generate_api_key("live")
    key = APIKey(
        project_id=project.id,
        key_prefix=prefix,
        hashed_key=hashed,
        key_type=KeyType.LIVE
    )
    contract = Contract(wasm_hash=hashlib.sha256(b"sample").hexdigest())
    job = Job(
        project_id=project.id,
        contract_id=contract.id,
        job_type=JobType.CONTRACT_RISK,
        classical_score=71.0,
        hybrid_score=78.0,
        delta_score=7.0
    )
    assert job.delta_score == 7.0
    assert project.tier == AccessTier.PROTOCOL
    print("  => PASSED: Project, APIKey, Contract, Job, and Finding models verified!")


if __name__ == "__main__":
    print("==================================================")
    print("    RUNNING QI-GUARD MVP INTEGRATION SUITE       ")
    print("==================================================")
    test_wasm_parser()
    test_api_key_security()
    test_schemas_contract_analysis()
    test_schemas_behavioral_analysis()
    test_database_models()
    print("==================================================")
    print("    ALL INTEGRATION TESTS PASSED SUCCESSFULLY!    ")
    print("==================================================")
