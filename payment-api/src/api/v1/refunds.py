from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from src.core.pagination import PaginatedPage
from src.models.domain.refund import Refund
from src.schemas.v1.crud.refunds import RefundOperationSchema, RefundSchema
from src.services.bearer import security_jwt
from src.services.refund import RefundQueryServiceABC, RefundServiceABC

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedPage[RefundSchema],
    description="Выдача список возвратов пользователя",
    summary="Выдача список возвратов пользователя",
    response_description="Постраничный вывод возвратов пользователей",
    tags=["Возвраты платежей"],
)
async def get_refunds(
    refund_query_service: RefundQueryServiceABC = Depends(),
    user: Annotated[UUID, Depends(security_jwt)] = None,
) -> PaginatedPage[Refund]:
    return await refund_query_service.gets(account_id=user)


@router.post(
    "/",
    response_model=RefundSchema,
    description="Осуществить возврат средств за подписку",
    summary="Осуществить возврат средств за подписку",
    response_description="Информация о возврате",
    tags=["Возвраты платежей"],
)
async def make_refund(
    refund_data: RefundOperationSchema,
    refund_service: RefundServiceABC = Depends(),
    user: Annotated[UUID, Depends(security_jwt)] = None,
) -> Refund:
    return await refund_service.refund(
        payment_id=refund_data.payment_id, description=refund_data.description
    )
