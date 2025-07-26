#!/usr/bin/env bash
set -euo pipefail

CI_MODE=false
if [[ ${1:-} == "--ci" ]]; then
  CI_MODE=true
fi

if ! command -v docker >/dev/null; then
  echo "SKIPPED – Docker not available"
  exit 0
fi

export DOCKER_BUILDKIT=1
CACHE_ARGS="--cache-from=type=gha --cache-to=type=gha,mode=max"

docker build --target runtime $CACHE_ARGS -t trading-platform . --progress=plain

CONTAINER=trading-test
docker run -d --rm --name $CONTAINER -p 5000:5000 -e POLYGON_API_KEY=dummy trading-platform

cleanup() {
  if [ "$CI_MODE" = true ]; then
    docker logs $CONTAINER || true
  fi
  docker stop $CONTAINER || true
}
trap cleanup EXIT

ready=0
for i in {1..30}; do
  if curl -fs http://localhost:5000/api/metrics | grep -q '"status":"ready"'; then
    ready=1
    break
  fi
  sleep 6
done

if [ $ready -ne 1 ]; then
  echo "Container failed to become ready within 180 seconds"
  exit 1
fi

docker exec $CONTAINER python -m trading_platform.run_daily --verify-only
