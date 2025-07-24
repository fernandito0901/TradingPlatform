# Runbook

1. Install requirements: `pip install -r requirements.txt`
2. Run tests: `pytest -q`
3. Format code: `black .`
4. Lint: `flake8`
5. Execute daily pipeline: `python -m trading_platform.run_daily --symbols AAPL`
