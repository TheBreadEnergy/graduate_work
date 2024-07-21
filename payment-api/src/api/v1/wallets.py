from typing import Annotated, Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from src.models.domain.wallet import Wallet
from src.schemas.v1.crud.wallets import WalletMakePrefferableSchema, WalletSchema
from src.services.bearer import security_jwt
from src.services.wallet import WalletQueryServiceABC, WalletServiceABC

router = APIRouter()


@router.get(
    "/wallet",
    response_model=list[WalletSchema],
    description="Получить сведения о платежном средстве",
    summary="Получить сведения о платежном средстве",
    response_description="Информация о платежном средстве",
    tags=["Платежная информация"],
)
async def get_payment_method(
    wallet_query_service: WalletQueryServiceABC = Depends(),
    user: Annotated[UUID, Depends(security_jwt)] = None,
) -> Sequence[Wallet]:
    return await wallet_query_service.get_wallet(account_id=user)


@router.put(
    "/wallet/{wallet_id}",
    response_model=WalletSchema,
    description="Сделать метод оплаты предпочтительным или нет",
    summary="Сделать метод оплаты предпочтительным или нет",
    response_description="Информация о платежном средстве",
    tags=["Платежная информация"],
)
async def set_preffer_payment_method(
    wallet_id: UUID,
    data: WalletMakePrefferableSchema,
    wallet_query_service: WalletServiceABC = Depends(),
    user: Annotated[UUID, Depends(security_jwt)] = None,
) -> Wallet:
    return await wallet_query_service.make_wallet_preffered(
        wallet_id=wallet_id, preferred=data.preferrable, account_id=user
    )
