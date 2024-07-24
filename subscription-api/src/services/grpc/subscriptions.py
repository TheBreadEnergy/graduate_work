from uuid import UUID

import grpc.aio
from grpc import StatusCode
from sqlalchemy import select
from src.core.grpc.models import subscription_pb2
from src.core.grpc.services.subscription_pb2_grpc import SubscriptionManagerServicer
from src.database.models import user_subscription_table
from src.database.postgres import async_session
from src.models.domain.user_subscription import UserSubscription


class GrpcUserSubscriptionManager(SubscriptionManagerServicer):
    async def GetSubscription(
        self,
        request: subscription_pb2.SubscriptionRequest,
        context: grpc.aio.ServicerContext,
    ) -> subscription_pb2.SubscriptionResponse:
        async with async_session() as session:
            user_subscription_query = select(UserSubscription).where(
                user_subscription_table.c.id == UUID(request.subscription_id)
            )
            try:
                result = await session.execute(user_subscription_query)
            except Exception as e:
                context.set_code(StatusCode.ABORTED)
                context.set_details(str(e))
            else:
                user_subscription = result.scalar_one_or_none()
                if not user_subscription:
                    context.set_code(StatusCode.NOT_FOUND)
                    context.set_details("Подписка у пользователя не обнаружена")
                    return
                response = subscription_pb2.SubscriptionResponse(
                    subscription_id=user_subscription.subscription.id,
                    subscription_name=user_subscription.subscription.name,
                    price=user_subscription.price,
                    currency=user_subscription.currency,
                )
                return response
