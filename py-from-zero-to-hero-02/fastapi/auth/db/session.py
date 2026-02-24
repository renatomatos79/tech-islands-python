from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from auth.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    # connects the session to the db engine
    bind=engine,
    # uses async sessions, not regular ones
    class_=AsyncSession,
    # default value is true, using false, objects remain usable after commit without re-fetching
    expire_on_commit=False,
    # we must call await session.flush() manually
    # it prevents unexpected writes with pore predictable behavior and performance control
    autoflush=False,
    # we must explicitly call "await session.commit()"
    autocommit=False,
)