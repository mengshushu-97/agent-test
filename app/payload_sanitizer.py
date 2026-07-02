from collections.abc import Iterable, Mapping
import json
import re
from typing import Any

MAX_LENGTH = 4096
SENSITIVE_KEYS = {
    "authorization",
    "access_token",
    "accessToken",
    "apiKey",
    "api_key",
    "key",
    "password",
    "passwd",
    "refresh_token",
    "refreshToken",
    "secret",
    "token",
}


def _is_sensitive_key(key: str) -> bool:
    return key in SENSITIVE_KEYS or re.search(
        r"password|token|secret|authorization|api[-_]?key",
        key,
        flags=re.IGNORECASE,
    ) is not None


def _truncate(value: str) -> str:
    if len(value) <= MAX_LENGTH:
        return value
    return f"{value[:MAX_LENGTH]}...[TRUNCATED]"


def sanitize(value: Any, depth: int = 0) -> Any:
    if value is None:
        return None
    if depth > 8:
        return "[MAX_DEPTH]"
    if isinstance(value, bytes):
        return sanitize(value.decode("utf-8", errors="replace"), depth)
    if isinstance(value, str):
        return _sanitize_string(value, depth)
    if isinstance(value, Mapping):
        return {
            str(key): "[REDACTED]" if _is_sensitive_key(str(key)) else sanitize(item, depth + 1)
            for key, item in value.items()
        }
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, bytearray)):
        return [sanitize(item, depth + 1) for item in value]
    return value


def _sanitize_string(value: str, depth: int) -> Any:
    stripped = value.strip()
    if not stripped:
        return ""
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            return sanitize(json.loads(stripped), depth + 1)
        except json.JSONDecodeError:
            return _truncate(value)
    return _truncate(value)
