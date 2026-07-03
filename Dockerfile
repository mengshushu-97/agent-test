FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
ENV PIP_TRUSTED_HOST=mirrors.aliyun.com

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-deps .

COPY scripts ./scripts
RUN chmod +x /app/scripts/start.sh \
    && useradd --create-home --shell /usr/sbin/nologin appuser

USER appuser
EXPOSE 8000

CMD ["/app/scripts/start.sh"]
