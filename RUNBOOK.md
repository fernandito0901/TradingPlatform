# Runbook

1. Install requirements: `pip install -r requirements.txt`
2. Run tests: `pytest -q`
3. Format code: `black .`
4. Lint: `flake8`
5. Execute daily pipeline: `python -m trading_platform.run_daily --symbols AAPL`
6. Copy `.env.example` to `.env` and provide values for required variables like
   `POLYGON_API_KEY`, `NEWS_API_KEY`, `REDIS_URL` and `SLACK_WEBHOOK_URL`. Optional
   values include `CACHE_TTL`, `SCHED_INTERVAL` and `HEALTH_PORT`.
7. Start services with `docker compose up --build`.
