from datetime import datetime, timezone
import json
import os
import sys
from typing import Any

try:
    from opentelemetry import trace
except ImportError:  # pragma: no cover
    trace = None

from app.config import get_settings


def _trace_fields() -> dict[str, str]:
    if trace is None:
        return {}
    span = trace.get_current_span()
    if span is None:
        return {}
    context = span.get_span_context()
    if not context or not context.is_valid:
        return {}
    return {
        "traceId": format(context.trace_id, "032x"),
        "spanId": format(context.span_id, "016x"),
    }


def _json_default(value: Any) -> str:
    if isinstance(value, Exception):
        return str(value)
    return repr(value)


def log(level: str, event: str, message: str, **fields: Any) -> None:
    settings = get_settings()
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "service": settings.service_name,
        "env": settings.app_env,
        "event": event,
        "message": message,
        **_trace_fields(),
        **fields,
    }
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, default=_json_default) + "\n")
    sys.stdout.flush()


def info(event: str, message: str, **fields: Any) -> None:
    log("info", event, message, **fields)


def warning(event: str, message: str, **fields: Any) -> None:
    log("warn", event, message, **fields)


def error(event: str, message: str, **fields: Any) -> None:
    if os.getenv("LOG_STACK") != "true" and "error" in fields:
        fields["error"] = str(fields["error"])
    log("error", event, message, **fields)
