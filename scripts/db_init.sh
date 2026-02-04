#!/usr/bin/env bash
# 기동 중인 MySQL에 jobs 테이블 생성 (init은 컨테이너 최초 1회만 실행되므로, 이미 볼륨이 있으면 이 스크립트로 적용)
set -euo pipefail
cd "$(dirname "$0")/.."

COMPOSE_FILE="${COMPOSE_FILE:-docker/docker-compose.yml}"

if ! docker compose -f "$COMPOSE_FILE" ps mysql 2>/dev/null | grep -q Up; then
  echo "MySQL이 기동 중이 아닙니다. 먼저: docker compose -f $COMPOSE_FILE up -d"
  exit 1
fi

echo "Applying docker/mysql/init/001_init.sql to MySQL..."
docker compose -f "$COMPOSE_FILE" exec -T mysql mysql -uroot -proot model_serving < docker/mysql/init/001_init.sql
echo "Done. jobs 테이블이 생성되었습니다."
