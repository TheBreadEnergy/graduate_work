import decimal
from abc import ABC, abstractmethod
from uuid import UUID

import grpc
from src.core.grpc.models import subscription_pb2
from src.core.grpc.services import subscription_pb2_grpc
from src.core.settings import settings
from src.exceptions.external import ExternalServiceUnavailableException
from src.schemas.v1.billing.subscription import Subscription


class SubscriptionManagerABC(ABC):
    @abstractmethod
    async def get_subscription(self, *, subscription_id: UUID) -> Subscription:
        ...


class SubscriptionManager(SubscriptionManagerABC):
    async def get_subscription(self, *, subscription_id: UUID) -> Subscription:
        async with grpc.insecure_channel(settings.subscription_address) as channel:
            stub = subscription_pb2_grpc.SubscriptionManagerStub(channel)
            request = subscription_pb2.SubscriptionRequest(
                subscription_id=str(subscription_id)
            )
            try:
                result: subscription_pb2.SubscriptionResponse = stub.GetSubscription(
                    request
                )
                return Subscription(
                    subscription_id=result.subscription_id,
                    subscription_name=result.subscription_name,
                    price=decimal.Decimal(result.price),
                    currency=result.currency,
                )
            except grpc.RpcError as e:
                raise ExternalServiceUnavailableException(
                    "Недоступен сервис подписки"
                ) from e
