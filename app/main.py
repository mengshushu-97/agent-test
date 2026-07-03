from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

from app.config import get_settings
from app.http_client import JavaClient
from app import logger
from app.payload_sanitizer import sanitize
from app.scheduler import start_scheduler, stop_scheduler
from app.tracing import setup_tracing


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _request_id(payload: dict[str, Any] | None) -> str:
    if payload and payload.get("requestId"):
        return str(payload["requestId"])
    return str(uuid.uuid4())


def create_app(dependencies: dict[str, Any] | None = None) -> FastAPI:
    dependencies = dependencies or {}
    settings = dependencies.get("settings") or get_settings()
    java_client = dependencies.get("java_client") or JavaClient(settings)

    @asynccontextmanager
    async def lifespan(app_instance: FastAPI):
        task = start_scheduler(settings)
        try:
            yield
        finally:
            await stop_scheduler(task)

    app = FastAPI(title="agent-test", lifespan=lifespan)
    setup_tracing(app)

    logger.info(
        "chain.received",
        "start success"
    )


    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        started_at = datetime.now(timezone.utc)
        request_body = await request.body()

        async def receive():
            return {
                "type": "http.request",
                "body": request_body,
                "more_body": False,
            }

        request_for_handler = Request(request.scope, receive)
        response = await call_next(request_for_handler)
        response_chunks = []
        async for chunk in response.body_iterator:
            response_chunks.append(chunk if isinstance(chunk, bytes) else chunk.encode("utf-8"))
        response_body = b"".join(response_chunks)
        duration_ms = (datetime.now(timezone.utc) - started_at).total_seconds() * 1000
        logger.info(
            "http.request",
            "request completed",
            method=request.method,
            path=request.url.path,
            query=sanitize(dict(request.query_params)),
            requestBody=sanitize(request_body),
            responseBody=sanitize(response_body),
            statusCode=response.status_code,
            durationMs=round(duration_ms, 2),
        )
        headers = dict(response.headers)
        headers.pop("content-length", None)
        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=headers,
            background=response.background,
        )

    @app.exception_handler(Exception)
    async def handle_exception(request: Request, exc: Exception):
        logger.error(
            "http.error",
            "request failed",
            method=request.method,
            path=request.url.path,
            statusCode=500,
            error=exc,
        )
        return JSONResponse(
            status_code=500,
            content={
                "service": settings.service_name,
                "status": "error",
                "message": str(exc),
                "timestamp": _now(),
            },
        )

    @app.get("/health")
    async def health():
        return {
            "service": settings.service_name,
            "status": "ok",
            "timestamp": _now(),
        }

    @app.get("/api/data")
    async def data():
        return {
            "source": settings.service_name,
            "value": "agent-data",
            "timestamp": _now(),
        }

    @app.post("/api/process")
    async def process(payload: dict[str, Any] | None = None):
        request_id = _request_id(payload)
        logger.info(
            "chain.received",
            "agent processed incoming request",
            requestId=request_id,
            chain=payload.get("chain") if payload else None,
            source=payload.get("source") if payload else None,
        )
        return {
            "source": settings.service_name,
            "requestId": request_id,
            "received": payload or {},
            "result": "processed",
            "timestamp": _now(),
        }

    @app.post("/api/java-agent-java")
    async def java_agent_java(payload: dict[str, Any] | None = None):
        request_id = _request_id(payload)
        logger.info(
            "chain.received",
            "java requested agent to call java",
            requestId=request_id,
            chain="java->agent->java",
        )

        java = await java_client.agent_data()
        return {
            "source": settings.service_name,
            "chain": "java->agent->java",
            "requestId": request_id,
            "received": payload or {},
            "java": java,
            "timestamp": _now(),
        }

    return app


app = create_app()
