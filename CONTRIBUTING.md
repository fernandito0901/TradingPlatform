# Contributing

Thanks for your interest in improving TradingPlatform! To get started:

1. Fork the repo and create a feature branch.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run `black .`, `flake8` and `pytest -q` before committing.
4. Update `CHANGELOG.md` and relevant docs for user-facing changes.
5. Open a pull request targeting `main`.

CI runs linting, tests and a Docker smoke test. If Docker is unavailable the
smoke step is skipped neutrally.
