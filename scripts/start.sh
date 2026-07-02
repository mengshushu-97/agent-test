#!/usr/bin/env sh
set -eu

export SERVICE_NAME="${SERVICE_NAME:-agent-test}"
export OTEL_SERVICE_NAME="${OTEL_SERVICE_NAME:-$SERVICE_NAME}"
export OTEL_EXPORTER_OTLP_PROTOCOL="${OTEL_EXPORTER_OTLP_PROTOCOL:-http/protobuf}"

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
