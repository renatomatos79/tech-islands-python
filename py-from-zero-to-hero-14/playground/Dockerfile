FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U uv

COPY . /app
RUN uv sync

EXPOSE 8000 6274 6277

ENV APP_PORT=8000
ENV HOST=0.0.0.0

CMD ["uv","run","mcp","dev","main.py"]
