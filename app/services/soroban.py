"""
Soroban JSON-RPC Client for fetching contract code, state entries, and ledger context.
"""

import httpx
import asyncio
import base64
from typing import Dict, Any, Optional
from app.config import settings


class SorobanRPCClient:
    def __init__(self, rpc_url: str = settings.SOROBAN_RPC_URL):
        self.rpc_url = rpc_url

    async def _json_rpc_call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes a JSON-RPC request to Soroban RPC node."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(self.rpc_url, json=payload)
                if response.status_code == 200:
                    return response.json().get("result", {})
            except Exception as e:
                # Return empty fallback on offline RPC
                return {"error": str(e)}
        return {}

    async def get_health(self) -> str:
        """Checks Soroban RPC node health status."""
        res = await self._json_rpc_call("getHealth")
        return res.get("status", "unhealthy")

    async def get_contract_wasm(self, contract_id: str) -> Optional[bytes]:
        """
        Retrieves deployed WASM bytecode for a given Soroban contract address.
        Returns bytes or None if contract WASM not found.
        """
        # Call getLedgerEntries for contract code key
        res = await self._json_rpc_call("getLedgerEntries", {"keys": [contract_id]})
        entries = res.get("entries", [])
        if entries:
            val_xdr = entries[0].get("xdr")
            if val_xdr:
                try:
                    return base64.b64decode(val_xdr)
                except Exception:
                    pass
        return None


soroban_rpc_client = SorobanRPCClient()
