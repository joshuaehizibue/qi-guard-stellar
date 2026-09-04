"""
Synchronous and Asynchronous client implementations for QI-Guard.
"""

import base64
import os
import time
from typing import Optional, Dict, Any, Union
import httpx

from qi_guard.models import (
    ContractRiskReport,
    BehavioralAnalysisReport,
    QuantumResilienceReport,
    BenchmarkReport
)
from qi_guard.exceptions import (
    QIGuardAPIError,
    QIGuardAuthenticationError,
    QIGuardRateLimitError,
    QIGuardError
)

DEFAULT_BASE_URL = "https://stellar.quantuminfra.io/v1"


def _handle_error_response(response: httpx.Response):
    status = response.status_code
    try:
        body = response.json()
        detail = body.get("detail", body.get("message", response.text))
    except Exception:
        body = response.text
        detail = response.text

    if status in (401, 403):
        raise QIGuardAuthenticationError(f"Authentication failed: {detail}", status, body)
    elif status == 429:
        raise QIGuardRateLimitError(f"Rate limit exceeded: {detail}", status, body)
    else:
        raise QIGuardAPIError(detail, status, body)


class QIGuardClient:
    """
    Synchronous client for the QI-Guard Quantum Security API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        http_client: Optional[httpx.Client] = None
    ):
        self.api_key = api_key or os.getenv("QIGUARD_API_KEY", "")
        self.base_url = (base_url or os.getenv("QIGUARD_API_URL", DEFAULT_BASE_URL)).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self._client = http_client or httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout
        )
        self._owns_client = http_client is None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self._owns_client:
            self._client.close()

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        attempt = 0
        delay = 0.3
        req_headers = dict(kwargs.get("headers") or {})
        if self.api_key and "Authorization" not in req_headers:
            req_headers["Authorization"] = f"Bearer {self.api_key}"
        kwargs["headers"] = req_headers
        url = f"{self.base_url}/{path.lstrip('/')}"

        while True:
            attempt += 1
            try:
                resp = self._client.request(method, url, **kwargs)
                if resp.is_success:
                    return resp.json()
                if resp.status_code in (429, 503) and attempt <= self.max_retries:
                    time.sleep(delay)
                    delay *= 2
                    continue
                _handle_error_response(resp)
            except httpx.RequestError as e:
                if attempt <= self.max_retries:
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise QIGuardError(f"Transport error connecting to QI-Guard: {str(e)}") from e

    def analyze_contract(
        self,
        wasm_bytes: Optional[bytes] = None,
        wasm_byte_code: Optional[str] = None,
        contract_address: Optional[str] = None,
        source_code_url: Optional[str] = None,
        network: str = "testnet"
    ) -> ContractRiskReport:
        """
        Submits Soroban WASM bytecode or contract address for quantum vulnerability analysis.
        """
        encoded_wasm = wasm_byte_code
        if wasm_bytes is not None and not encoded_wasm:
            encoded_wasm = base64.b64encode(wasm_bytes).decode("utf-8")

        payload = {"network": network}
        if encoded_wasm:
            payload["wasm_byte_code"] = encoded_wasm
        if contract_address:
            payload["contract_address"] = contract_address
        if source_code_url:
            payload["source_code_url"] = source_code_url

        data = self._request("POST", "/analyze/contract", json=payload)
        return ContractRiskReport.model_validate(data)

    def analyze_behavioral(
        self,
        address: str,
        analysis_window: str = "7d",
        transactions: Optional[list] = None
    ) -> BehavioralAnalysisReport:
        """
        Submits a Stellar address for behavioral anomaly analysis.
        """
        payload = {
            "address": address,
            "analysis_window": analysis_window,
            "transactions": transactions or []
        }
        data = self._request("POST", "/analyze/behavioral", json=payload)
        return BehavioralAnalysisReport.model_validate(data)

    def get_resilience(self, target: str) -> QuantumResilienceReport:
        """
        Retrieves post-quantum cryptographic resilience readiness score for an account/contract.
        """
        data = self._request("GET", f"/resilience/{target}")
        return QuantumResilienceReport.model_validate(data)

    def get_benchmark(self, job_id: str) -> BenchmarkReport:
        """
        Retrieves side-by-side classical vs. hybrid model metrics for an audit job.
        """
        data = self._request("GET", f"/benchmarks/{job_id}")
        return BenchmarkReport.model_validate(data)

    def get_usage(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves project monthly usage and remaining quota.
        """
        params = {"project_id": project_id} if project_id else {}
        return self._request("GET", "/billing/usage", params=params)


class AsyncQIGuardClient:
    """
    Asynchronous client for the QI-Guard Quantum Security API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        http_client: Optional[httpx.AsyncClient] = None
    ):
        self.api_key = api_key or os.getenv("QIGUARD_API_KEY", "")
        self.base_url = (base_url or os.getenv("QIGUARD_API_URL", DEFAULT_BASE_URL)).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self._client = http_client or httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout
        )
        self._owns_client = http_client is None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if self._owns_client:
            await self._client.aclose()

    async def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        attempt = 0
        delay = 0.3
        import asyncio
        req_headers = dict(kwargs.get("headers") or {})
        if self.api_key and "Authorization" not in req_headers:
            req_headers["Authorization"] = f"Bearer {self.api_key}"
        kwargs["headers"] = req_headers
        url = f"{self.base_url}/{path.lstrip('/')}"

        while True:
            attempt += 1
            try:
                resp = await self._client.request(method, url, **kwargs)
                if resp.is_success:
                    return resp.json()
                if resp.status_code in (429, 503) and attempt <= self.max_retries:
                    await asyncio.sleep(delay)
                    delay *= 2
                    continue
                _handle_error_response(resp)
            except httpx.RequestError as e:
                if attempt <= self.max_retries:
                    await asyncio.sleep(delay)
                    delay *= 2
                    continue
                raise QIGuardError(f"Transport error connecting to QI-Guard: {str(e)}") from e

    async def analyze_contract(
        self,
        wasm_bytes: Optional[bytes] = None,
        wasm_byte_code: Optional[str] = None,
        contract_address: Optional[str] = None,
        source_code_url: Optional[str] = None,
        network: str = "testnet"
    ) -> ContractRiskReport:
        encoded_wasm = wasm_byte_code
        if wasm_bytes is not None and not encoded_wasm:
            encoded_wasm = base64.b64encode(wasm_bytes).decode("utf-8")

        payload = {"network": network}
        if encoded_wasm:
            payload["wasm_byte_code"] = encoded_wasm
        if contract_address:
            payload["contract_address"] = contract_address
        if source_code_url:
            payload["source_code_url"] = source_code_url

        data = await self._request("POST", "/analyze/contract", json=payload)
        return ContractRiskReport.model_validate(data)

    async def analyze_behavioral(
        self,
        address: str,
        analysis_window: str = "7d",
        transactions: Optional[list] = None
    ) -> BehavioralAnalysisReport:
        payload = {
            "address": address,
            "analysis_window": analysis_window,
            "transactions": transactions or []
        }
        data = await self._request("POST", "/analyze/behavioral", json=payload)
        return BehavioralAnalysisReport.model_validate(data)

    async def get_resilience(self, target: str) -> QuantumResilienceReport:
        data = await self._request("GET", f"/resilience/{target}")
        return QuantumResilienceReport.model_validate(data)

    async def get_benchmark(self, job_id: str) -> BenchmarkReport:
        data = await self._request("GET", f"/benchmarks/{job_id}")
        return BenchmarkReport.model_validate(data)

    async def get_usage(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"project_id": project_id} if project_id else {}
        return await self._request("GET", "/billing/usage", params=params)
