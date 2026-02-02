FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U uv

COPY . /app
RUN uv sync

EXPOSE 8000 6274 6277

ENV APP_PORT=8000
ENV MCP_MODE=run
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0

CMD ["sh", "-lc", "\
  set -eux; \
  echo \"MCP_MODE=${MCP_MODE} APP_PORT=${APP_PORT}\"; \
  if [ \"${MCP_MODE}\" = \"dev\" ]; then \
    exec uv run mcp dev main_dev.py; \
  else \
    exec uv run python -u main_http.py; \
  fi \
"]
