from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from src.core.pagination import PaginatedPage
from src.models.domain.subscription import Subscription
from src.schemas.user import Roles, UserDto
from src.schemas.v1.subscription import SubscriptionCreateSchema, SubscriptionSchema
from src.services.bearer import require_roles, security_jwt
from src.services.subscription import (
    SubscriptionQueryServiceABC,
    SubscriptionServiceABC,
)

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedPage[SubscriptionSchema],
    description="Вывести доступные подписки",
    summary="Вывести доступные подписки",
    response_description="Страница заданного размера с доступными подписками",
    tags=["Подписки"],
)
async def get_subscriptions(
    subscription_query_service: SubscriptionQueryServiceABC = Depends(),
) -> PaginatedPage[Subscription]:
    return await subscription_query_service.get_subscriptions()


@router.get(
    "/{subscription_id}",
    response_model=SubscriptionSchema,
    description="Получить данные о подписке",
    summary="Получить данные о подписке",
    response_description="Сведения о подписке",
    tags=["Подписки"],
)
async def get_subscription(
    subscription_id: UUID,
    subscription_query_service: SubscriptionQueryServiceABC = Depends(),
) -> Subscription:
    return await subscription_query_service.get_subscription(
        subscription_id=subscription_id
    )


@router.post(
    "/",
    response_model=SubscriptionSchema,
    description="Добавить подписку",
    summary="Добавить подписку",
    response_description="Сведения о добавленной подписке",
    tags=["Подписки"],
)
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def create_subscription(
    data: SubscriptionCreateSchema,
    subscription_service: SubscriptionServiceABC = Depends(),
    user: Annotated[UserDto, Depends(security_jwt)] = None,
) -> Subscription:
    return await subscription_service.create_subscription(subscription_data=data)


@router.put(
    "/{subscription_id}",
    response_model=SubscriptionSchema,
    description="Изменить сведения о подписке",
    summary="Изменить сведения о подписке",
    response_description="Сведения об обновленной подписке",
    tags=["Подписки"],
)
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def update_subscription(
    subscription_id: UUID,
    subscription_data: SubscriptionCreateSchema,
    subscription_service: SubscriptionServiceABC = Depends(),
    user: Annotated[UserDto, Depends(security_jwt)] = None,
) -> Subscription:
    return await subscription_service.update_subscription(
        subscription_id=subscription_id, subscription_data=subscription_data
    )


@router.delete(
    "/{subscription_id}",
    description="Удалить подписку",
    summary="Удалить подписку",
    tags=["Подписки"],
)
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def delete_subscription(
    subscription_id: UUID,
    subscription_service: SubscriptionServiceABC = Depends(),
    user: Annotated[UserDto, Depends(security_jwt)] = None,
):
    return await subscription_service.delete_subscription(
        subscription_id=subscription_id
    )
