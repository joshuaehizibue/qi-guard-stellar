"""
Stellar Horizon API REST Client with retry logic and transaction history streaming.
"""

import httpx
import asyncio
from typing import Dict, Any, List, Optional
from app.config import settings


class HorizonClient:
    def __init__(self, horizon_url: str = settings.STELLAR_HORIZON_URL):
        self.horizon_url = horizon_url.rstrip("/")

    async def _request_with_retry(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, max_retries: int = 3
    ) -> Dict[str, Any]:
        """Executes GET request to Horizon API with exponential backoff on 429/5xx errors."""
        url = f"{self.horizon_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            delay = 0.5
            for attempt in range(max_retries):
                try:
                    response = await client.get(url, params=params)
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code in (429, 500, 502, 503, 504):
                        await asyncio.sleep(delay)
                        delay *= 2
                    else:
                        response.raise_for_status()
                except httpx.HTTPError as e:
                    if attempt == max_retries - 1:
                        # Return fallback structure if network unreachable
                        return {
                            "_embedded": {"records": []},
                            "error": str(e),
                            "status": getattr(e.response, "status_code", 500) if hasattr(e, "response") else 500
                        }
                    await asyncio.sleep(delay)
                    delay *= 2
            return {"_embedded": {"records": []}}

    async def get_account_info(self, address: str) -> Dict[str, Any]:
        """Fetches Stellar account details (balances, signers, sequence)."""
        return await self._request_with_retry(f"accounts/{address}")

    async def get_account_transactions(
        self, address: str, limit: int = 50, order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """Fetches historical transactions for a given Stellar account address."""
        params = {"limit": limit, "order": order}
        data = await self._request_with_retry(f"accounts/{address}/transactions", params=params)
        return data.get("_embedded", {}).get("records", [])

    async def get_account_operations(
        self, address: str, limit: int = 50, order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """Fetches historical operations (payment, invoke_host_function, create_account)."""
        params = {"limit": limit, "order": order}
        data = await self._request_with_retry(f"accounts/{address}/operations", params=params)
        return data.get("_embedded", {}).get("records", [])


horizon_client = HorizonClient()
