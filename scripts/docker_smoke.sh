#!/usr/bin/env bash
set -euo pipefail

CI_MODE=false
ART_DIR=""
if [[ ${1:-} == "--ci" ]]; then
  CI_MODE=true
  ART_DIR="artifacts"
fi

if ! command -v docker >/dev/null; then
  echo "SKIPPED – Docker not available"
  exit 99
fi

export DOCKER_BUILDKIT=1
CACHE_ARGS="--cache-from=type=gha --cache-to=type=gha,mode=max"

docker build --target runtime $CACHE_ARGS -t trading-platform . --progress=plain

CONTAINER=trading-test
docker run -d --rm --name $CONTAINER -p 5000:5000 -e POLYGON_API_KEY=dummy trading-platform

cleanup() {
  status=$?
  if [ "$CI_MODE" = true ]; then
    docker logs $CONTAINER || true
    if [ -n "$ART_DIR" ]; then
      mkdir -p "$ART_DIR"
      docker logs $CONTAINER >"$ART_DIR/smoke.log" 2>&1 || true
    fi
  fi
  docker stop $CONTAINER || true
  exit $status
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
