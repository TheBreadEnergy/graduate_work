from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.core.settings import settings

engine = create_async_engine(
    str(settings.database_conn), echo=settings.echo, future=True
)

async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
