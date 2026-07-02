FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir .

COPY scripts ./scripts
RUN chmod +x /app/scripts/start.sh \
    && useradd --create-home --shell /usr/sbin/nologin appuser

USER appuser
EXPOSE 8000

CMD ["/app/scripts/start.sh"]
