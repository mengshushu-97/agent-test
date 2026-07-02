import unittest

import io
import json
from contextlib import redirect_stdout

import httpx

from app.main import create_app


class AgentApiContractTest(unittest.IsolatedAsyncioTestCase):
    async def test_health_endpoint_returns_agent_service_status(self):
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service"], "agent-test")
        self.assertEqual(response.json()["status"], "ok")

    async def test_process_endpoint_returns_agent_contract(self):
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post("/api/process", json={"source": "node-test"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["source"], "agent-test")
        self.assertEqual(response.json()["received"]["source"], "node-test")

    async def test_http_request_log_includes_path_input_and_output(self):
        stream = io.StringIO()
        transport = httpx.ASGITransport(app=create_app())

        with redirect_stdout(stream):
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.post(
                    "/api/process?debug=true",
                    json={"requestId": "req-log-test", "password": "secret-value"},
                )

        self.assertEqual(response.status_code, 200)

        logs = [json.loads(line) for line in stream.getvalue().splitlines() if line]
        http_log = next(
            item for item in logs
            if item["event"] == "http.request" and item["path"] == "/api/process"
        )

        self.assertEqual(http_log["query"]["debug"], "true")
        self.assertEqual(http_log["requestBody"]["requestId"], "req-log-test")
        self.assertEqual(http_log["requestBody"]["password"], "[REDACTED]")
        self.assertEqual(http_log["responseBody"]["source"], "agent-test")
        self.assertEqual(http_log["responseBody"]["received"]["requestId"], "req-log-test")


if __name__ == "__main__":
    unittest.main()
