from typing import Annotated

from fastapi import APIRouter, Depends, Query
from src.core.pagination import PaginatedPage
from src.models.domain.user_subscription import UserSubscription
from src.schemas.user import Roles, UserDto
from src.schemas.v1.user_subscription import UserSubscriptionSchema
from src.services.bearer import require_roles, security_jwt
from src.services.user_subscription import UserSubscriptionQueryServiceABC

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedPage[UserSubscriptionSchema],
    description="Вывести список пользовательских подписок",
    summary="Вывести список пользовательских подписок",
    response_description="Пагинированный список пользовательских подписок",
    tags=["Пользовательские подписки"],
)
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def get_all_subscriptions(
    active: Annotated[bool | None, Query(description="С активной подпиской")] = None,
    user_subscription_query_service: UserSubscriptionQueryServiceABC = Depends(),
    user: Annotated[UserDto, Depends(security_jwt)] = None,
) -> PaginatedPage[UserSubscription]:
    return await user_subscription_query_service.get_all_user_subscriptions(
        active=active
    )


@router.get(
    "/user",
    response_model=PaginatedPage[UserSubscriptionSchema],
    description="Вывести список пользовательских подписок",
    summary="Вывести список пользовательских подписок",
    response_description="Пагинированный список пользовательских подписок",
    tags=["Пользовательские подписки"],
)
async def get_user_subscriptions(
    active: Annotated[bool | None, Query(description="С активной подпиской")] = None,
    user_subscription_query_service: UserSubscriptionQueryServiceABC = Depends(),
    user: Annotated[UserDto, Depends(security_jwt)] = None,
) -> PaginatedPage[UserSubscription]:
    return await user_subscription_query_service.get_user_subscriptions(
        account_id=user.id, active=active
    )
