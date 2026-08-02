# syntax=docker/dockerfile:1.7

FROM python:3.13-slim-bookworm AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY backend/pyproject.toml ./
COPY backend/src ./src

RUN python -m pip install --upgrade pip build \
    && python -m build --wheel --outdir /wheels

FROM python:3.13-slim-bookworm AS runtime

ARG APP_UID=10001
ARG APP_GID=10001
ARG VCS_REF=unknown
ARG BUILD_DATE=unknown

LABEL org.opencontainers.image.title="Cloud Content Hub API" \
      org.opencontainers.image.description="Cloud Content Hub FastAPI runtime" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.source="https://github.com/${GITHUB_REPOSITORY:-unknown}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/home/cch/.local/bin:${PATH}" \
    PORT=8000

RUN groupadd --gid "${APP_GID}" cch \
    && useradd --uid "${APP_UID}" --gid cch --create-home --shell /usr/sbin/nologin cch

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY --chown=cch:cch backend/alembic.ini ./alembic.ini
COPY --chown=cch:cch backend/migrations ./migrations
RUN python -m pip install /wheels/*.whl \
    && rm -rf /wheels

USER cch

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\", \"8000\")}/health/live', timeout=3)"]

CMD ["sh", "-c", "exec uvicorn cloud_content_hub.main:app --host 0.0.0.0 --port \"$PORT\" --proxy-headers --forwarded-allow-ips='*'"]

FROM runtime AS dev

USER root
COPY backend/pyproject.toml ./
COPY backend/src ./src
RUN python -m pip install --no-cache-dir --editable ".[dev]"
USER cch

CMD ["sh", "-c", "exec uvicorn cloud_content_hub.main:app --host 0.0.0.0 --port \"$PORT\" --reload --reload-dir /app/src"]

FROM runtime AS test

USER root
COPY backend/pyproject.toml ./
COPY backend/src ./src
COPY backend/tests ./tests
RUN python -m pip install --no-cache-dir --editable ".[dev]"
USER cch

CMD ["pytest"]
