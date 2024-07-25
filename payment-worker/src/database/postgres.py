from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings

engine_payments = create_async_engine(
    str(settings.database_conn_payments), echo=settings.echo, future=True
)

engine_subscriptions = create_async_engine(
    str(settings.database_conn_subscriptions), echo=settings.echo, future=True
)

async_session_payments = async_sessionmaker(
    bind=engine_payments, class_=AsyncSession, expire_on_commit=False
)

async_session_subscriptions = async_sessionmaker(
    bind=engine_subscriptions, class_=AsyncSession, expire_on_commit=False
)


async def get_session(async_session) -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
