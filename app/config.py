from dataclasses import dataclass
import os


def _int_from_env(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default
    return value if value > 0 else default


@dataclass(frozen=True)
class Settings:
    service_name: str
    app_env: str
    port: int
    java_service_url: str
    request_timeout_ms: int
    heartbeat_interval_ms: int


def get_settings() -> Settings:
    return Settings(
        service_name=os.getenv("SERVICE_NAME", os.getenv("OTEL_SERVICE_NAME", "agent-test")),
        app_env=os.getenv("APP_ENV", "local"),
        port=_int_from_env("PORT", 8000),
        java_service_url=os.getenv("JAVA_SERVICE_URL", "http://localhost:8080"),
        request_timeout_ms=_int_from_env("REQUEST_TIMEOUT_MS", 5000),
        heartbeat_interval_ms=_int_from_env("HEARTBEAT_INTERVAL_MS", 1000),
    )
