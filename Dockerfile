# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app

FROM base AS builder
COPY requirements.txt ./
COPY pyproject.toml ./
COPY src ./src
COPY features ./features
COPY models ./models
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e . && \
    python -c "import trading_platform.reports.scoreboard"

FROM base AS runtime
ARG APP_USER=appuser
RUN useradd -u 1001 -r -s /bin/false $APP_USER
COPY --from=builder /usr/local /usr/local
COPY src ./src
COPY features ./features
COPY models ./models
COPY requirements.txt ./
COPY pyproject.toml ./
COPY scripts ./scripts
COPY run_pipeline.sh ./run_pipeline.sh
ENV REPORTS_DIR=/app/reports
RUN mkdir -p ${REPORTS_DIR} && \
    chown -R ${APP_USER}:${APP_USER} ${REPORTS_DIR}
USER $APP_USER
CMD ["./run_pipeline.sh"]
