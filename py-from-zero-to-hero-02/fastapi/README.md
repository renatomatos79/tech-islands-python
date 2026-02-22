uv add --dev "uvicorn[standard]"

docker compose up -d
uv run python -m uvicorn app.main:app --reload

http://127.0.0.1:8001/docs



docker compose up --build
http://localhost:8001/docs