import asyncio
import logging
from datetime import datetime, timezone

from src.broker.rabbit import RabbitMessageBroker
from src.core.config import settings
from src.database.postgres import get_session
from src.schemas.notify import NotificationMessage
from src.service import get_subscriptions_to_notify, update_last_notified


async def main():
    while True:
        logging.info(f"Начало процесса: {datetime.now(timezone.utc)}")
        async for session in get_session():
            broker = RabbitMessageBroker(
                host=settings.rabbit_host,
                port=settings.rabbit_port,
                username=settings.rabbit_login,
                password=settings.rabbit_password,
            )
            await broker.startup()

            async for subscriptions in get_subscriptions_to_notify(session):
                messages = [
                    NotificationMessage(
                        user_id=sub.user_id,
                        subscription_id=sub.id,
                        message="Ваша подписка истекает через 5 дней.",
                    ).json()
                    for sub in subscriptions
                ]
                logging.info(f"Отправка сообщений: {messages}")
                await broker.publish_notifications(messages)

                subscription_ids = [sub.id for sub in subscriptions]
                await update_last_notified(session, subscription_ids)

            await broker.shutdown()
            logging.info(f"Конец процесса: {datetime.now(timezone.utc)}")
            # Спим 12 часов
            await asyncio.sleep(12 * 60 * 60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
