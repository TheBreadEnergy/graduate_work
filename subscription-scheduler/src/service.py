import logging
from datetime import datetime, timedelta

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_subscription import UserSubscription

logger = logging.getLogger(__name__)


async def get_subscriptions_to_notify(
    session: AsyncSession, subscription_duration_days: int = 30, batch_size: int = 1000
):
    today = datetime.utcnow().date()
    offset = 0

    while True:
        async with session.begin():
            result = await session.execute(
                select(UserSubscription)
                .where(
                    UserSubscription.active.is_(True),
                    func.date(
                        UserSubscription.last_payed
                        + timedelta(days=subscription_duration_days)
                        - timedelta(days=5)
                    )
                    <= today,
                    or_(
                        UserSubscription.last_notified < UserSubscription.last_payed,
                        UserSubscription.last_notified.is_(None),
                    ),
                )
                .offset(offset)
                .limit(batch_size)
            )
            subscriptions = result.scalars().all()
            if not subscriptions:
                break
            logger.info(f"Найдены для уведомлений подписки: {len(subscriptions)}")
            yield subscriptions
            offset += batch_size


async def update_last_notified(session: AsyncSession, subscription_ids: list):
    await session.execute(
        update(UserSubscription)
        .where(UserSubscription.id.in_(subscription_ids))
        .values(last_notified=datetime.utcnow())
    )
