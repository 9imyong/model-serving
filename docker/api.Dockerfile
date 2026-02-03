# - uv로 의존성 설치(빌드 스테이지에서만)
# - 런타임은 가볍게
# - Gunicorn + UvicornWorker로 FastAPI 구동
#
# 전제:
# - pyproject.toml / uv.lock 존재
# - 앱 엔트리: app.main:app (네 트리 기준)

# ---------- builder ----------
FROM python:3.11-slim AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

# 핵심: uv sync가 /opt/venv에 설치하도록 강제
RUN uv venv /opt/venv \
    && . /opt/venv/bin/activate \
    && uv sync --frozen --no-dev --active


# ---------- runtime ----------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# builder에서 만든 venv 복사
COPY --from=builder /opt/venv /opt/venv

# 앱 소스 복사
COPY app ./app
# COPY gunicorn.conf.py ./gunicorn.conf.py

EXPOSE 8000

# 헬스체크(선택): /health 엔드포인트가 있다고 가정
# (curl이 없으면 Python으로 체크하거나, K8s probe에서 처리)
# HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health').read()"

# CMD ["gunicorn", "app.main:app", "-c", "app.gunicorn.conf.py"]
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
