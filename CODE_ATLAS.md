# Code Atlas

Summary of key modules and functions in the project.

| Module | Description |
| ------ | ----------- |
| `features.pipeline` | Feature engineering pipeline with `compute_features`, `from_db` and `run_pipeline`. |
| `models.train` | LightGBM training via `train`. |
| `playbook.generate` | Build JSON playbook with `generate_playbook`. |
| `collector.api` | REST API calls to Polygon. |
| `collector.db` | SQLite schema helpers. |
| `collector.verify` | Preflight connectivity check. |
| `reports.dashboard` | Generate HTML dashboard of AUC metrics. |
