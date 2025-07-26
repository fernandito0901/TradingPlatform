train:
	python -m trading_platform.models.train $(ARGS)

tune:
	python -m trading_platform.models.train --tune $(ARGS)

backtest:
	python scripts/run_backtest.py $(ARGS)

daily:
	python -m trading_platform.run_daily $(ARGS)

docker-smoke:
	scripts/docker_smoke.sh --ci || { CODE=$$?; [ $$CODE -eq 78 ] || exit $$CODE; }
