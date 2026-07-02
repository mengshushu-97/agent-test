from typing import Any

import httpx

try:
    from opentelemetry.propagate import inject
except ImportError:  # pragma: no cover
    inject = None

from app.config import Settings


def _trace_headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    if inject is not None:
        inject(headers)
    return headers


class JavaClient:
    def __init__(self, settings: Settings):
        self._settings = settings

    async def agent_data(self) -> dict[str, Any]:
        timeout = self._settings.request_timeout_ms / 1000
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                f"{self._settings.java_service_url}/api/agent/data",
                headers=_trace_headers(),
            )
            response.raise_for_status()
            return response.json()
