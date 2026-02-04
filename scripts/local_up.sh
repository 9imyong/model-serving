#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# 인프라만 기동 (MySQL, Kafka, Redis). API/Worker는 로컬에서 uv로 실행.
docker compose -f docker/docker-compose.yml up -d
echo ""
echo "인프라 기동 완료. API/Worker는 다음처럼 로컬에서 실행:"
echo "  export MYSQL_HOST=localhost KAFKA_BOOTSTRAP_SERVERS=localhost:9092 REDIS_HOST=localhost"
echo "  uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000   # API"
echo "  uv run python -m app.worker.main                                   # Worker"
