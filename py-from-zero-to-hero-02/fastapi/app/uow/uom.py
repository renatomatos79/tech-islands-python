from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.uom import UnitOfMeasurement

async def get_all(session: AsyncSession) -> list[UnitOfMeasurement]:
    res = await session.execute(select(UnitOfMeasurement).order_by(UnitOfMeasurement.id))
    return list(res.scalars().all())

async def get_by_id(session: AsyncSession, uom_id: int) -> UnitOfMeasurement | None:
    return await session.get(UnitOfMeasurement, uom_id)

async def get_by_code(
    session: AsyncSession, code: str, exclude_id: int | None = None
) -> UnitOfMeasurement | None:
    stmt = select(UnitOfMeasurement).where(UnitOfMeasurement.code == code)
    if exclude_id is not None:
        stmt = stmt.where(UnitOfMeasurement.id != exclude_id)
    res = await session.execute(stmt.limit(1))
    return res.scalar_one_or_none()

async def get_by_name(
    session: AsyncSession, name: str, exclude_id: int | None = None
) -> UnitOfMeasurement | None:
    stmt = select(UnitOfMeasurement).where(UnitOfMeasurement.name == name)
    if exclude_id is not None:
        stmt = stmt.where(UnitOfMeasurement.id != exclude_id)
    res = await session.execute(stmt.limit(1))
    return res.scalar_one_or_none()

async def create(session: AsyncSession, name: str, code: str) -> UnitOfMeasurement:
    obj = UnitOfMeasurement(name=name, code=code)
    session.add(obj)
    await session.flush()
    return obj

async def update(session: AsyncSession, obj: UnitOfMeasurement, name: str | None, code: str | None) -> UnitOfMeasurement:
    if name is not None:
        obj.name = name
    if code is not None:
        obj.code = code
    await session.flush()
    return obj

async def delete(session: AsyncSession, obj: UnitOfMeasurement) -> None:
    await session.delete(obj)
