from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app import models  # noqa: F401

from app.api.routes.uom import router as uom_router
from app.api.routes.sku import router as sku_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # For production: use Alembic migrations instead of create_all.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Inventory API (Async SQLAlchemy + Postgres)",
    lifespan=lifespan,
)

app.include_router(uom_router)
app.include_router(sku_router)
