from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sku import Sku

async def get_all(session: AsyncSession) -> list[Sku]:
    res = await session.execute(select(Sku).order_by(Sku.id))
    return list(res.scalars().all())

async def get_by_id(session: AsyncSession, sku_id: int) -> Sku | None:
    return await session.get(Sku, sku_id)

async def get_by_code(session: AsyncSession, code: str, exclude_id: int | None = None) -> Sku | None:
    stmt = select(Sku).where(Sku.code == code)
    if exclude_id is not None:
        stmt = stmt.where(Sku.id != exclude_id)
    res = await session.execute(stmt.limit(1))
    return res.scalar_one_or_none()

async def get_by_description(
    session: AsyncSession, description: str, exclude_id: int | None = None
) -> Sku | None:
    stmt = select(Sku).where(Sku.description == description)
    if exclude_id is not None:
        stmt = stmt.where(Sku.id != exclude_id)
    res = await session.execute(stmt.limit(1))
    return res.scalar_one_or_none()

async def create(session: AsyncSession, code: str, description: str, unit_price: float, uom_id: int) -> Sku:
    obj = Sku(code=code, description=description, unit_price=unit_price, uom_id=uom_id)
    session.add(obj)
    await session.flush()
    return obj

async def update(
    session: AsyncSession,
    obj: Sku,
    code: str | None,
    description: str | None,
    unit_price: float | None,
    uom_id: int | None,
) -> Sku:
    if code is not None:
        obj.code = code
    if description is not None:
        obj.description = description
    if unit_price is not None:
        obj.unit_price = unit_price
    if uom_id is not None:
        obj.uom_id = uom_id
    await session.flush()
    return obj

async def delete(session: AsyncSession, obj: Sku) -> None:
    await session.delete(obj)
