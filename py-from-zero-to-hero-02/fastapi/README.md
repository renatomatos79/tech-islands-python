<p align="center">
  <img src="./imgs/swagger.png" alt="Swagger" width="900" />
</p>


# Quick Setup

# Let's build our first FastAPI

## Add a new folder `py-from-zero-to-hero-02`
```bash
mkdir py-from-zero-to-hero-02
cd py-from-zero-to-hero-02
```

## Create this project folder and enter it
```bash
mkdir fastapi
cd fastapi
```

## Initialize the project with `uv`
```bash
uv init
```

## Add dependencies
```bash
uv add fastapi sqlalchemy asyncpg pydantic pydantic-settings
uv add --dev "uvicorn[standard]"
```

## (Optional) create and sync virtual environment
```bash
uv sync --group dev
```

# (1) Running this API locally

## (1.1) Start PostgreSQL with Docker Compose
```bash
docker compose up -d
```

## (1.2) Run the API in reload mode
```bash
uv run python -m uvicorn app.main:app --reload --port 8001
```

## (1.3) Open Swagger
- Docs: http://127.0.0.1:8001/docs
- OpenAPI JSON: http://127.0.0.1:8001/openapi.json

# (2) Project configuration

## (2.1) Environment and settings
This project uses `pydantic-settings` (`app/core/config.py`) and reads:

- `DATABASE_URL`

Default local value:
```text
postgresql+asyncpg://app:app@localhost:5432/inventorydb
```

For Docker Compose app container, `DATABASE_URL` is set to:
```text
postgresql+asyncpg://app:app@db:5432/inventorydb
```

## (2.2) Database session
`app/db/session.py` creates:
- async SQLAlchemy engine
- `AsyncSessionLocal`

`app/api/deps.py` provides one session per request.

## (2.3) Startup behavior
`app/main.py` loads models for mapper registration and runs:
- `Base.metadata.create_all(...)` on startup

Note: for production, prefer Alembic migrations.

# (3) API entities

## (3.1) Unit of Measurement (UOM)
Table: `unit_of_measurements`
- `id`
- `code` (unique)
- `name` (unique)

## (3.2) SKU
Table: `skus`
- `id`
- `code` (unique)
- `description`
- `unit_price`
- `uom_id` (FK -> `unit_of_measurements.id`)

# (4) Validation rules implemented

## UOM
- Create/update validates unique `code`
- Create/update validates unique `name` (description)
- Delete is blocked when any SKU uses the UOM (`409`)

## SKU
- Create/update validates unique `code`
- Create/update validates unique `description`
- Create/update validates that `uom_id` exists

# (5) Endpoints

## UOM
- `GET /unit-of-measurements`
- `POST /unit-of-measurements`
- `PUT /unit-of-measurements/{uom_id}`
- `DELETE /unit-of-measurements/{uom_id}`

## SKU
- `GET /skus` (returns nested UOM object)
- `POST /skus`
- `PUT /skus/{sku_id}`
- `DELETE /skus/{sku_id}`

# (6) Docker

## (6.1) Dockerfile
This project Dockerfile uses `uv` (not `pip`) and installs dependencies from:
- `pyproject.toml`
- `uv.lock`

It starts the API with:
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## (6.2) Docker Compose
`docker-compose.yml` includes:
- `db` (PostgreSQL 16)
- `api` (builds from local Dockerfile)

Run:
```bash
docker compose up --build
```

Open:
- http://127.0.0.1:8001/docs

# (7) Useful commands

## Recreate database from scratch
```bash
docker compose down -v
docker compose up -d
```

## Stop everything
```bash
docker compose down
```

## Run only API locally (DB already running)
```bash
uv run python -m uvicorn app.main:app --reload --port 8001
```

# (8) Comming soon

In the next version, we will add an authentication API with these endpoints:

- `POST /api/auth/register`
- `POST /api/auth/token`

After login, the API will issue a JWT access token.  
Protected endpoints will require a valid JWT in the `Authorization: Bearer <token>` header.
