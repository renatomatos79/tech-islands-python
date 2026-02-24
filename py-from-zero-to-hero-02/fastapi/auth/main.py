from contextlib import asynccontextmanager
from importlib import import_module

from fastapi import FastAPI
from auth.db.session import engine
from auth.db.base import Base

# Ensure SQLAlchemy model mappers are registered at startup.
import_module("auth.models")

from auth.api.routes.auth import router as auth_router

@asynccontextmanager
async def lifespan(_app: FastAPI):
    _ = _app  # FastAPI passes the app instance; keep explicit to satisfy Pylance.
    # =>>>> For production: lets use "Alembic migrations" instead of "create_all".
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Auth API (Async SQLAlchemy + Postgres)",
    lifespan=lifespan,
)

app.include_router(auth_router)