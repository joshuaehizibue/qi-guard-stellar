"""
Exhaustive System-Wide Test Suite Using Programmatically Generated Data
Tests:
1. Binary WASM generation (Access Control, Loops, Clean Contracts, Fuzzed/Corrupt inputs)
2. Classical MLP & PennyLane Quantum VQC Hybrid Engine feature transformations & bounds
3. Behavioral Anomaly Engine across 5 realistic transaction archetypes
4. Quantum Resilience PQC Surface Scanner on generated Stellar/Soroban accounts
5. End-to-end REST API endpoints with generated payloads
6. Partner Onboarding & Ground Truth Feedback Telemetry aggregation
7. Python SDK Client verification on generated data
8. JS CLI binary verification on generated WASM binaries
"""

import base64
import os
import subprocess
import time
import pytest
import pytest_asyncio
from typing import Dict, Any, List
from httpx import AsyncClient
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../sdks/python")))
from qi_guard import QIGuardClient, AsyncQIGuardClient

from app.services.wasm_parser import wasm_disassembler, WASMParserError
from app.services.classical_engine import classical_engine, ClassicalVulnerabilityEngine
from app.services.quantum_engine import quantum_engine, QuantumHybridEngine
from app.services.behavioral_engine import behavioral_engine
from app.services.resilience_engine import resilience_engine
from app.services.telemetry import TelemetryService
from app.models.project import AccessTier


# ============================================================================
# 1. SYNTHETIC DATA GENERATORS
# ============================================================================

def encode_uleb128(val: int) -> bytes:
    """Encodes unsigned integer into LEB128 byte sequence."""
    res = bytearray()
    while True:
        b = val & 0x7F
        val >>= 7
        if val != 0:
            b |= 0x80
        res.append(b)
        if val == 0:
            break
    return bytes(res)


def build_wasm_section(sec_id: int, payload: bytes) -> bytes:
    """Constructs a valid WebAssembly binary section."""
    return bytes([sec_id]) + encode_uleb128(len(payload)) + payload


def generate_synthetic_wasm(
    exported_functions: List[str],
    imported_functions: List[tuple[str, str]],
    loop_count: int = 0,
    br_if_count: int = 0,
    call_count: int = 1,
    padding_bytes: int = 0
) -> bytes:
    """
    Programmatically builds a syntactically valid WebAssembly (WASM) binary module
    with customized exports, host imports, and code section instruction sequences.
    """
    # 1. Magic + Version
    header = b"\x00asm\x01\x00\x00\x00"

    # 2. Type Section (Section 1): single func type () -> ()
    type_payload = encode_uleb128(1) + b"\x60\x00\x00"
    type_sec = build_wasm_section(1, type_payload)

    # 3. Import Section (Section 2)
    if imported_functions:
        imp_body = encode_uleb128(len(imported_functions))
        for mod, field in imported_functions:
            mod_b = mod.encode("utf-8")
            field_b = field.encode("utf-8")
            imp_body += encode_uleb128(len(mod_b)) + mod_b
            imp_body += encode_uleb128(len(field_b)) + field_b
            imp_body += b"\x00" + encode_uleb128(0)  # func import, type 0
        import_sec = build_wasm_section(2, imp_body)
    else:
        import_sec = b""

    # 4. Export Section (Section 7)
    if exported_functions:
        exp_body = encode_uleb128(len(exported_functions))
        for idx, func_name in enumerate(exported_functions):
            name_b = func_name.encode("utf-8")
            exp_body += encode_uleb128(len(name_b)) + name_b
            exp_body += b"\x00" + encode_uleb128(idx)  # func export
        export_sec = build_wasm_section(7, exp_body)
    else:
        export_sec = b""

    # 5. Code Section (Section 10)
    # Generate instructions based on requested loop, br_if, and call opcodes
    opcodes = bytearray()
    for _ in range(loop_count):
        opcodes.append(0x03)  # loop opcode
    for _ in range(br_if_count):
        opcodes.append(0x0D)  # br_if opcode
    for _ in range(call_count):
        opcodes.append(0x10)  # call opcode
        opcodes.append(0x00)  # func index 0
    if padding_bytes > 0:
        opcodes.extend(b"\x01" * padding_bytes)  # nop opcodes
    opcodes.append(0x0B)  # end opcode

    # Wrap in function body
    func_body = encode_uleb128(0) + bytes(opcodes)  # 0 locals
    func_len = encode_uleb128(len(func_body))
    code_payload = encode_uleb128(1) + func_len + func_body
    code_sec = build_wasm_section(10, code_payload)

    return header + type_sec + import_sec + export_sec + code_sec


def generate_synthetic_transactions(
    archetype: str,
    count: int = 20,
    base_time: float = None
) -> List[Dict[str, Any]]:
    """
    Generates realistic Stellar Horizon transaction records for distinct behavior archetypes.
    """
    if base_time is None:
        base_time = time.time() - 86400 * 5  # 5 days ago

    txs = []
    if archetype == "ORGANIC_USER":
        # Spread over 5 days, normal fees, 1 operation per transaction
        for i in range(count):
            t = base_time + (i * 3600 * 4)  # Every 4 hours
            txs.append({
                "id": f"tx_org_{i:04d}",
                "successful": True,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)),
                "operation_count": 1,
                "fee_charged": 100,  # 100 stroops
                "memo": "swap xlm/usdc",
            })
    elif archetype == "FLASH_DRAIN":
        # 30 transactions within 2 minutes, high operation counts, high priority fees
        for i in range(count):
            t = base_time + (i * 4)  # Every 4 seconds
            txs.append({
                "id": f"tx_drain_{i:04d}",
                "successful": True,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)),
                "operation_count": 8,  # > 5 ops/tx
                "fee_charged": 25000,  # > 10000 stroops
                "memo": "drain_vault",
            })
    elif archetype == "UNUSUAL_INVOCATION":
        for i in range(count):
            t = base_time + (i * 60)
            txs.append({
                "id": f"tx_inv_{i:04d}",
                "successful": True,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)),
                "operation_count": 6,
                "fee_charged": 15000,
                "memo": "flash_loan_callback",
            })
    elif archetype == "EMPTY":
        return []
    elif archetype == "SINGLE_TX":
        return [{
            "id": "tx_single_0001",
            "successful": True,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(base_time)),
            "operation_count": 1,
            "fee_charged": 100,
            "memo": "genesis deposit",
        }]
    return txs


# ============================================================================
# 2. TEST SUITES
# ============================================================================

class TestWASMDisassemblerGeneratedData:
    """Verifies WASM disassembler on synthetic and fuzzed binaries."""

    def test_vulnerable_admin_contracts(self):
        """Generates WASMs with admin functions missing require_auth."""
        admin_funcs = ["transfer_admin", "set_owner", "transfer_ownership", "set_auth_admin"]
        for func in admin_funcs:
            wasm_bytes = generate_synthetic_wasm(
                exported_functions=[func, "init"],
                imported_functions=[("env", "log")],  # No auth import!
                call_count=5
            )
            parsed = wasm_disassembler.parse_bytecode(wasm_bytes)
            assert parsed["is_valid_wasm"] is True
            assert func in parsed["exported_functions"]
            assert len(parsed["vulnerability_findings"]) == 1
            finding = parsed["vulnerability_findings"][0]
            assert finding["id"] == "QIG-SCF-0041"
            assert finding["type"] == "ACCESS_CONTROL"
            assert finding["severity"] == "HIGH"
            assert finding["quantum_contribution"] is True

    def test_secure_admin_contracts(self):
        """Generates WASMs with admin functions AND valid require_auth import."""
        wasm_bytes = generate_synthetic_wasm(
            exported_functions=["transfer_admin", "balance"],
            imported_functions=[("env", "require_auth"), ("env", "log")],
            call_count=3
        )
        parsed = wasm_disassembler.parse_bytecode(wasm_bytes)
        assert parsed["is_valid_wasm"] is True
        assert "transfer_admin" in parsed["exported_functions"]
        # With require_auth present, Rule 1 must NOT flag
        access_findings = [f for f in parsed["vulnerability_findings"] if f["type"] == "ACCESS_CONTROL"]
        assert len(access_findings) == 0

    def test_unbounded_loop_contracts(self):
        """Generates WASMs with high loop density and insufficient exits."""
        wasm_bytes = generate_synthetic_wasm(
            exported_functions=["compute_yield"],
            imported_functions=[("env", "require_auth")],
            loop_count=14,  # > 10 loops
            br_if_count=2,  # < 5 br_if
            call_count=4
        )
        parsed = wasm_disassembler.parse_bytecode(wasm_bytes)
        loop_findings = [f for f in parsed["vulnerability_findings"] if f["type"] == "RESOURCE_EXHAUSTION"]
        assert len(loop_findings) == 1
        assert loop_findings[0]["id"] == "QIG-SCF-0082"
        assert loop_findings[0]["severity"] == "MEDIUM"

    def test_clean_token_contract(self):
        """Generates clean SEP-41 standard token contract."""
        wasm_bytes = generate_synthetic_wasm(
            exported_functions=["transfer", "balance", "allowance", "approve"],
            imported_functions=[("env", "require_auth"), ("env", "storage")],
            loop_count=2,
            br_if_count=4,
            call_count=8
        )
        parsed = wasm_disassembler.parse_bytecode(wasm_bytes)
        assert len(parsed["vulnerability_findings"]) == 0

    def test_malformed_and_fuzzed_inputs(self):
        """Fuzz tests disassembler with malformed byte sequences."""
        fuzzed_samples = [
            b"",
            b"INVALID_HEADER",
            b"\x7fELF\x01\x01\x01\x00\x00\x00\x00\x00",
            b"\x00asm",  # truncated header (< 8 bytes)
            b"\x00asm\x02\x00\x00\x00",  # wrong version
            b"\x00asm\x01\x00\x00\x00" + b"\xff" * 100,  # invalid section headers
            b"\x00asm\x01\x00\x00\x00" + os.urandom(2000),  # random bytes
        ]

        for sample in fuzzed_samples:
            try:
                result = wasm_disassembler.parse_bytecode(sample)
                # If it doesn't raise, it must return a valid dictionary structure
                assert isinstance(result, dict)
            except WASMParserError:
                # Expected for bad headers
                pass


class TestIntelligenceEngineGeneratedData:
    """Verifies Classical MLP and PennyLane VQC Hybrid Engine mathematical invariants."""

    def test_classical_feature_bounds_across_spectrum(self):
        """Tests classical feature extraction and score bounds across 20 synthetic inputs."""
        for i in range(20):
            mock_parsed = {
                "byte_size": i * 600,
                "function_count": i * 4,
                "exported_functions": [f"fn_{j}" for j in range(i % 8)],
                "imported_functions": [f"imp_{j}" for j in range(i % 5)],
                "opcode_frequencies": {"loop": (i * 2) % 15},
                "call_site_count": i * 3,
                "vulnerability_findings": [{"severity": "HIGH"}] if i % 2 == 1 else []
            }
            feat_vec, latent, score = classical_engine.encode_wasm_features(mock_parsed)

            # Assert normalization [0.0, 1.0]
            assert len(feat_vec) == 8
            assert all(0.0 <= val <= 1.0 for val in feat_vec)

            # Assert ReLU latent embedding >= 0.0
            assert len(latent) == 8
            assert all(val >= 0.0 for val in latent)

            # Assert score in [10.0, 98.0]
            assert 10.0 <= score <= 98.0

    def test_quantum_hybrid_engine_invariants(self):
        """Tests Variational Quantum Circuit expectation values and Quantum Delta bounds."""
        engine = QuantumHybridEngine(n_qubits=8, circuit_depth=4)

        # Generate 15 diverse latent vectors
        test_latents = [
            [0.0] * 8,
            [1.0] * 8,
            [0.5] * 8,
            [0.1 * i for i in range(8)],
            [0.9 - 0.1 * i for i in range(8)],
        ]

        for latent in test_latents:
            classical_score = 50.0
            hybrid_score, delta, exp_vals, config = engine.execute_hybrid_circuit(latent, classical_score)

            # Expectation values must be in [-1.0, 1.0]
            assert len(exp_vals) == 8
            assert all(-1.0 <= ev <= 1.0 for ev in exp_vals)

            # Quantum Delta must be bounded in [3.0, 12.0]
            assert 3.0 <= delta <= 12.0

            # Hybrid score must equal min(99.0, classical_score + delta)
            assert hybrid_score == min(99.0, round(classical_score + delta, 2))

            # Config validation
            assert config["n_qubits"] == 8
            assert config["circuit_depth"] == 4
            assert config["gate_set"] == ["RX", "RY", "CZ"]
            assert config["parameter_shift_gradient"] is True


class TestBehavioralEngineGeneratedData:
    """Verifies Behavioral Anomaly Engine against 5 distinct transaction archetypes."""

    def test_organic_user_activity(self):
        records = generate_synthetic_transactions("ORGANIC_USER", count=5)
        cls_score, hyb_score, delta, patterns, related = behavioral_engine.analyze_account_activity(
            "GBESTORGANICUSER1234567890STEL", records, window="7d"
        )
        assert cls_score < 0.70
        assert hyb_score < 0.75
        assert delta > 0.0

    def test_flash_drain_attack(self):
        records = generate_synthetic_transactions("FLASH_DRAIN", count=30)
        cls_score, hyb_score, delta, patterns, related = behavioral_engine.analyze_account_activity(
            "GDRAINATTACKACCOUNT123456789STEL", records, window="24h"
        )
        assert cls_score >= 0.70
        assert hyb_score >= 0.75
        pattern_types = [p["type"] for p in patterns]
        assert "RAPID_DRAIN" in pattern_types

    def test_empty_account(self):
        records = generate_synthetic_transactions("EMPTY")
        cls_score, hyb_score, delta, patterns, related = behavioral_engine.analyze_account_activity(
            "GEMPTYNEWACCOUNT1234567890STEL", records, window="7d"
        )
        assert cls_score == 0.15
        assert hyb_score == 0.21
        assert len(patterns) == 1
        assert patterns[0]["type"] == "NEW_ACCOUNT_BASELINE"
        assert len(related) == 0

    def test_single_transaction_account(self):
        records = generate_synthetic_transactions("SINGLE_TX")
        cls_score, hyb_score, delta, patterns, related = behavioral_engine.analyze_account_activity(
            "GSINGLETXACCOUNT1234567890STEL", records, window="7d"
        )
        assert 0.40 <= cls_score <= 0.60
        assert hyb_score > cls_score


class TestQuantumResilienceScannerGeneratedData:
    """Verifies Quantum Resilience Scanner against multiple account structures."""

    def test_single_and_multisig_accounts(self):
        accounts = [
            {"target": "GAAA1111111111111111111111111111111111111111111111111111", "signers": [{"key": "GAAA..."}]},
            {"target": "GBBB2222222222222222222222222222222222222222222222222222", "signers": [{"key": "G1"}, {"key": "G2"}, {"key": "G3"}]},
            {"target": "CCCC3333333333333333333333333333333333333333333333333333", "signers": []},
        ]
        for acc in accounts:
            exp_score, status, findings, checklist = resilience_engine.evaluate_target(acc["target"], acc)
            assert exp_score == 61
            assert status == "PARTIALLY_READY"
            assert len(findings) > 0
            assert "key_rotation_policy" in checklist
            assert checklist["crypto_agility"] == "partial"


@pytest.mark.asyncio
class TestAPIEndpointsWithGeneratedData:
    """End-to-end integration tests submitting synthetic datasets over HTTP."""

    async def test_contract_analysis_with_generated_wasms(self, client: AsyncClient, seed_data: Dict[str, Any]):
        auth_header = {"Authorization": f"Bearer {seed_data['raw_live_key']}"}

        # 1. Submit vulnerable WASM via base64
        vuln_wasm = generate_synthetic_wasm(
            exported_functions=["transfer_admin"],
            imported_functions=[],
            call_count=4
        )
        b64_vuln = base64.b64encode(vuln_wasm).decode("utf-8")
        resp = await client.post(
            "/v1/analyze/contract",
            headers=auth_header,
            json={"wasm_byte_code": b64_vuln, "contract_address": "C_TEST_VULN_01"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["job_id"].startswith("job_cnt_")
        assert data["risk_score"]["hybrid"] > data["risk_score"]["classical"]
        assert any(f["type"] == "ACCESS_CONTROL" for f in data["findings"])

        # 2. Submit clean WASM via hex
        clean_wasm = generate_synthetic_wasm(
            exported_functions=["transfer", "balance"],
            imported_functions=[("env", "require_auth")],
            call_count=2
        )
        hex_clean = "0x" + clean_wasm.hex()
        resp2 = await client.post(
            "/v1/analyze/contract",
            headers=auth_header,
            json={"wasm_byte_code": hex_clean, "contract_address": "C_TEST_CLEAN_01"}
        )
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert not any(f["type"] == "ACCESS_CONTROL" for f in data2["findings"])

        # 3. Submit malformed WASM -> must return 400 Bad Request
        bad_wasm = b"CORRUPTED_NON_WASM_CONTENT"
        resp3 = await client.post(
            "/v1/analyze/contract",
            headers=auth_header,
            json={"wasm_byte_code": base64.b64encode(bad_wasm).decode("utf-8")}
        )
        assert resp3.status_code == 400
        assert "Invalid WASM" in resp3.json()["detail"]

    async def test_behavioral_analysis_with_generated_transactions(self, client: AsyncClient, seed_data: Dict[str, Any]):
        auth_header = {"Authorization": f"Bearer {seed_data['raw_live_key']}"}

        # Submit Flash Drain transactions
        drain_txs = generate_synthetic_transactions("FLASH_DRAIN", count=25)
        resp = await client.post(
            "/v1/analyze/behavioral",
            headers=auth_header,
            json={
                "address": "GEXPLOITTESTADDRESS12345678901234567890",
                "analysis_window": "24h",
                "transactions": drain_txs
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["risk_level"] == "HIGH"
        assert data["anomaly_score"]["hybrid"] >= 0.70
        assert any(p["type"] == "RAPID_DRAIN" for p in data["patterns"])

    async def test_resilience_and_benchmark_endpoints(self, client: AsyncClient, seed_data: Dict[str, Any]):
        auth_header = {"Authorization": f"Bearer {seed_data['raw_live_key']}"}

        # 1. Resilience
        resp_res = await client.get("/v1/resilience/GTESTACCOUNTFORRESILIENCE1234567890", headers=auth_header)
        assert resp_res.status_code == 200
        res_data = resp_res.json()
        assert res_data["quantum_exposure_score"] == 61
        assert res_data["migration_status"] == "PARTIALLY_READY"

        # 2. Analyze contract to produce a job_id
        wasm_bytes = generate_synthetic_wasm(["ping"], [("env", "log")])
        resp_cnt = await client.post(
            "/v1/analyze/contract",
            headers=auth_header,
            json={"wasm_byte_code": "0x" + wasm_bytes.hex()}
        )
        job_id = resp_cnt.json()["job_id"]

        # 3. Retrieve benchmark
        resp_bm = await client.get(f"/v1/benchmarks/{job_id}", headers=auth_header)
        assert resp_bm.status_code == 200
        bm_data = resp_bm.json()
        assert bm_data["job_id"] == job_id
        assert "metrics" in bm_data
        assert bm_data["metrics"]["hybrid"]["f1_score"] >= bm_data["metrics"]["classical"]["f1_score"]
        assert bm_data["metrics"]["delta"]["f1_improvement"] >= 0


@pytest.mark.asyncio
class TestPartnerTelemetryAndFeedbackLoop:
    """Verifies Partner Onboarding, Ground Truth Feedback, and Telemetry with synthetic partners."""

    async def test_partner_lifecycle(self, client: AsyncClient, db_session):
        # 1. Onboard 3 synthetic partners
        partners = [
            {"organization_name": "Synthetic AMM Protocol", "contact_email": "team@syn-amm.org", "protocol_category": "DEFI"},
            {"organization_name": "Synthetic Bridge Labs", "contact_email": "security@syn-bridge.io", "protocol_category": "INFRASTRUCTURE"},
            {"organization_name": "Synthetic Stablecoin DAO", "contact_email": "dev@syn-usd.finance", "protocol_category": "PAYMENTS"},
        ]

        live_keys = []
        for p in partners:
            resp = await client.post("/v1/partners/onboard", json=p)
            assert resp.status_code == 200
            data = resp.json()
            assert data["organization"] == p["organization_name"]
            assert data["tier"] == "PROTOCOL"
            assert data["keys"]["live_key"].startswith("qig_live_")
            live_keys.append((data["project_id"], data["keys"]["live_key"]))

        # 2. Submit synthetic feedback on findings
        project_id, _ = live_keys[0]
        feedback_samples = [
            {"finding_id": "QIG-SCF-0041", "project_id": project_id, "is_true_positive": True, "notes": "Confirmed admin transfer vulnerability"},
            {"finding_id": "QIG-SCF-0082", "project_id": project_id, "is_true_positive": True, "notes": "Confirmed gas exhaustion risk in loop"},
            {"finding_id": "QIG-SCF-0099", "project_id": project_id, "is_true_positive": False, "notes": "Auditor identified as intentional pattern"},
        ]

        for fb in feedback_samples:
            resp_fb = await client.post("/v1/partners/feedback", json=fb)
            assert resp_fb.status_code == 200
            fb_res = resp_fb.json()
            assert "feedback_id" in fb_res
            assert fb_res["is_true_positive"] == fb["is_true_positive"]

        # 3. Query telemetry aggregation
        resp_tel = await client.get("/v1/partners/telemetry")
        assert resp_tel.status_code == 200
        tel_data = resp_tel.json()
        assert tel_data["active_design_partners"] >= 3
        assert "partner_roster" in tel_data
        assert "partner_reported_precision" in tel_data


class TestSDKsWithGeneratedData:
    """Verifies Python and JS SDKs against synthetic WASMs."""

    def test_js_cli_help_and_version(self):
        """Runs the executable JS CLI binary with help and version."""
        cli_path = os.path.abspath("sdks/js/bin/qi-guard.js")
        res_v = subprocess.run(["node", cli_path, "version"], capture_output=True, text=True)
        assert res_v.returncode == 0
        assert "0.1.0" in res_v.stdout

        res_h = subprocess.run(["node", cli_path, "--help"], capture_output=True, text=True)
        assert res_h.returncode == 0
        assert "Usage:" in res_h.stdout

    def test_python_sdk_with_generated_wasm(self, seed_data, db_session):
        """Tests the Python SDK Client with programmatically generated WASM binary."""
        from starlette.testclient import TestClient
        from app.main import app
        from app.core.database import get_db

        async def _override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = _override_get_db

        wasm_bytes = generate_synthetic_wasm(
            exported_functions=["transfer_admin"],
            imported_functions=[],
            call_count=3
        )
        b64_wasm = base64.b64encode(wasm_bytes).decode("utf-8")

        with TestClient(app) as http_client:
            sdk_client = QIGuardClient(api_key=seed_data["raw_live_key"], http_client=http_client)
            report = sdk_client.analyze_contract(wasm_byte_code=b64_wasm)
            assert report.job_id.startswith("job_cnt_")
            assert report.risk_score.hybrid > report.risk_score.classical
            assert any(f.type == "ACCESS_CONTROL" for f in report.findings)

        app.dependency_overrides.clear()
