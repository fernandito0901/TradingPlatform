# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app

FROM base AS builder
COPY requirements.txt ./
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

FROM base AS runtime
RUN useradd -u 1001 -r -s /bin/false appuser
COPY --from=builder /usr/local /usr/local
COPY src ./src
COPY requirements.txt ./
COPY pyproject.toml ./
COPY scripts ./scripts
COPY run_pipeline.sh ./run_pipeline.sh
USER 1001
CMD ["./run_pipeline.sh"]
