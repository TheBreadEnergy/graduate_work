from functools import cache

from src.dependencies.registrator import add_factory_to_mapper
from src.services.subscription import SubscriptionManager, SubscriptionManagerABC


@add_factory_to_mapper(SubscriptionManagerABC)
@cache
def create_subsription_manager() -> SubscriptionManager:
    return SubscriptionManager()
