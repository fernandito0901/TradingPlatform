#!/bin/bash
set -e
python -m trading_platform.collector.seed_scoreboard
python -m trading_platform.run_daily "$@"
