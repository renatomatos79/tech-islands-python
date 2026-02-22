from fastapi import FastAPI
from db.session import engine
from db.base import Base

from api.routes.uom import router as uoms_router
from api.routes.sku import router as skus_router

# Import models so metadata is registered
from models.uom import UnitOfMeasurement  # noqa: F401
from models.sku import Sku  # noqa: F401

app = FastAPI(title="Inventory API (Async SQLAlchemy + Postgres)")

app.include_router(uoms_router)
app.include_router(skus_router)

@app.on_event("startup")
async def on_startup():
    # For production: use Alembic migrations instead of create_all.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)