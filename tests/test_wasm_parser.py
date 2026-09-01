"""
Unit tests for the WASM Disassembler & Vulnerability Analyzer.
"""

import pytest
from app.services.wasm_parser import wasm_disassembler, WASMParserError


def test_wasm_parser_invalid_header():
    with pytest.raises(WASMParserError):
        wasm_disassembler.parse_bytecode(b"NOT_A_WASM_FILE")


def test_wasm_parser_valid_minimal_binary():
    # Valid WebAssembly binary header
    minimal_wasm = b"\x00asm\x01\x00\x00\x00\x01\x04\x01\x60\x00\x00\x02\x0a\x01\x03env\x04auth\x00\x00\x07\x13\x01\x0etransfer_admin\x00\x00\x0a\x04\x01\x02\x00\x0b"
    parsed = wasm_disassembler.parse_bytecode(minimal_wasm)
    
    assert parsed["is_valid_wasm"] is True
    assert "transfer_admin" in parsed["exported_functions"]
    assert len(parsed["vulnerability_findings"]) > 0
    finding = parsed["vulnerability_findings"][0]
    assert finding["id"] == "QIG-SCF-0041"
    assert finding["type"] == "ACCESS_CONTROL"
