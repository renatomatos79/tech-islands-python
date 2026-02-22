from contextlib import asynccontextmanager
from importlib import import_module

from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base

# Ensure SQLAlchemy model mappers are registered at startup.
import_module("app.models")

from app.api.routes.uom import router as uom_router
from app.api.routes.sku import router as sku_router

@asynccontextmanager
async def lifespan(_app: FastAPI):
    _ = _app  # FastAPI passes the app instance; keep explicit to satisfy Pylance.
    # =>>>> For production: lets use "Alembic migrations" instead of "create_all".
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Inventory API (Async SQLAlchemy + Postgres)",
    lifespan=lifespan,
)

app.include_router(uom_router)
app.include_router(sku_router)
