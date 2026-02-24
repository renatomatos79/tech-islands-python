from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models.user import User


async def get_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    res = await session.execute(stmt.limit(1))
    return res.scalar_one_or_none()


async def get_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    res = await session.execute(stmt.limit(1))
    return res.scalar_one_or_none()


async def create(session: AsyncSession, username: str, email: str, pwd_hash: str) -> User:
    obj = User(username=username, email=email, password_hash=pwd_hash)
    session.add(obj)
    await session.flush()
    return obj
