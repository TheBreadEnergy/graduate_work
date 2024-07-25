from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from src.core.pagination import PaginatedPage
from src.enums.payment import PaymentStatus
from src.models.domain.payment import Payment
from src.schemas.v1.billing.payments import PayStatusSchema
from src.schemas.v1.crud.payments import (
    PaymentOperationSchema,
    PaymentSchema,
    PaymentStatusSchema,
)
from src.services.bearer import security_jwt
from src.services.payment import PaymentQueryServiceABC, PaymentServiceABC

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedPage[PaymentSchema],
    description="Платежи сделанные пользователем",
    summary="Постраничный вывод платежей сделанный пользователем",
    response_description="Постраничный вывод платежей сделанный пользователем",
    tags=["Платежи"],
)
async def get_payments(
    payment_query_service: PaymentQueryServiceABC = Depends(),
    user: Annotated[UUID, Depends(security_jwt)] = None,
) -> PaginatedPage[Payment]:
    return await payment_query_service.get_payments(account_id=user)


@router.get(
    "/{payment_id}",
    response_model=PaymentSchema,
    description="Сведения об оплате",
    summary="Сведения об оплате",
    response_description="Информация о платеже",
    tags=["Платежи"],
)
async def get_payment(
    payment_id: UUID,
    payment_query_service: PaymentQueryServiceABC = Depends(),
    user: Annotated[UUID, Depends(security_jwt)] = None,
) -> Payment:
    payment = await payment_query_service.get_payment(payment_id=payment_id)
    if not payment.account_id != user:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="У вас недостаточно прав просматривать данный платеж",
        )
    return payment


@router.post(
    "/",
    response_model=PaymentStatusSchema,
    description="Провести оплату подписки",
    summary="Провести оплату подписки",
    response_description="Переадресация на платежную систему для продолжения платежа",
    tags=["Платежи"],
)
async def make_payment(
    payment_data: PaymentOperationSchema,
    payment_service: PaymentServiceABC = Depends(),
    user: Annotated[UUID, Depends(security_jwt)] = None,
) -> PayStatusSchema:
    operation_response: PayStatusSchema = await payment_service.make_payment(
        subscription_id=payment_data.subscription_id,
        subscription_name=payment_data.subscription_name,
        price=payment_data.price,
        currency=payment_data.currency.value,
        account_id=user,
        save_payment_method=payment_data.save_payment_method,
        payment_method=payment_data.payment_method.value,
    )
    if operation_response.status == PaymentStatus.cancelled:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=operation_response.reason
        )
    return operation_response
