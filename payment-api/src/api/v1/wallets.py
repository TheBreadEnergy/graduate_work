from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from src.models.domain.wallet import Wallet
from src.schemas.v1.crud.wallets import WalletSchema
from src.services.bearer import security_jwt
from src.services.wallet import WalletQueryServiceABC

router = APIRouter()


@router.get(
    "/wallet",
    response_model=WalletSchema,
    description="Получить сведения о платежном средстве",
    summary="Получить сведения о платежном средстве",
    response_description="Информация о платежном средстве",
    tags=["Платежная информация"],
)
async def get_payment_method(
    wallet_query_service: WalletQueryServiceABC = Depends(),
    user: Annotated[UUID, Depends(security_jwt)] = None,
) -> Wallet:
    return await wallet_query_service.get_wallet(account_id=user)
