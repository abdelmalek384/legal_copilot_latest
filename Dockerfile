FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Runtime dependencies are installed only from the reviewed, hash-locked set.
COPY requirements-py312.lock ./requirements-py312.lock
RUN python -m pip install --require-hashes -r requirements-py312.lock \
    && python -m pip check

# The application never runs as root. Persistent data is mounted separately.
RUN groupadd --system --gid 10001 legalcopilot \
    && useradd --system --uid 10001 --gid 10001 --home-dir /nonexistent \
       --shell /usr/sbin/nologin legalcopilot
COPY --chown=10001:10001 . /app

USER 10001:10001

EXPOSE 8000

# Liveness only; release readiness is governed by separate acceptance gates.
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=3).read(1)" || exit 1

# Do not trust forwarded headers by default.
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--no-proxy-headers", "--workers", "1", "--timeout-keep-alive", "5"]
