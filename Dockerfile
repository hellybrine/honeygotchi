FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# curl is used by the Docker HEALTHCHECK below. No ssh-keygen needed — the
# app generates its host key in-process with asyncssh.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY config.yaml ./config.yaml

RUN groupadd -r honeygotchi && useradd -r -g honeygotchi -u 10001 honeygotchi \
    && mkdir -p /app/logs /app/data \
    && chown -R honeygotchi:honeygotchi /app

USER honeygotchi

EXPOSE 2222 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8080/health || exit 1

CMD ["python", "-m", "src.honeygotchi"]
