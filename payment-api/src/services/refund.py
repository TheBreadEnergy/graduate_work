from abc import ABC, abstractmethod
from uuid import UUID

from src.core.pagination import PaginatedPage
from src.enums.payment import PaymentStatus
from src.exceptions.payment import PaymentNotFoundException
from src.exceptions.refund import RefundNotFoundException
from src.models.domain.refund import Refund
from src.models.events.refund import RefundCreatedEvent
from src.repositories.refunds import RefundRepositoryABC
from src.schemas.v1.crud.refunds import RefundCreateSchema
from src.services.billing.payment_gateway import PaymentGatewayABC
from src.services.event_handler import EventHandlerABC
from src.services.uow import UnitOfWorkABC


class RefundQueryServiceABC(ABC):
    @abstractmethod
    async def get_refunds_for_account(
        self, *, account_id: UUID
    ) -> PaginatedPage[Refund]:
        ...

    @abstractmethod
    async def get_refund(self, *, refund_id: UUID) -> Refund:
        ...


class RefundQueryService(RefundQueryServiceABC):
    def __init__(self, refund_repository: RefundRepositoryABC):
        self._refund_repository = refund_repository

    async def get_refunds_for_account(
        self, *, account_id: UUID
    ) -> PaginatedPage[Refund]:
        return await self._refund_repository.gets(account_id=account_id)

    async def get_refund(self, *, refund_id: UUID) -> Refund:
        refund = await self._refund_repository.get(entity_id=refund_id)
        if not refund:
            raise RefundNotFoundException()
        return refund

    async def filter_by_status(self, status: PaymentStatus) -> PaginatedPage[Refund]:
        return await self._refund_repository.filter_by_status(status=status)


class RefundServiceABC(ABC):
    @abstractmethod
    async def refund(self, payment_id: UUID, description: str | None = None) -> Refund:
        ...


class RefundService(RefundServiceABC):
    def __init__(
        self,
        payment_gateway: PaymentGatewayABC,
        event_handler: EventHandlerABC,
        uow: UnitOfWorkABC,
    ):
        self._gateway = payment_gateway
        self._handler = event_handler
        self._uow = uow

    async def refund(self, payment_id: UUID, description: str | None = None) -> Refund:
        async with self._uow:
            payment = await self._uow.payment_repository.get(entity_id=payment_id)
            if not payment:
                raise PaymentNotFoundException()
            status = self._gateway.create_refund(payment)
            refund_obj = RefundCreateSchema(
                account_id=payment.account_id,
                payment_id=payment_id,
                description=description or "",
                money=payment.price,
                status=status.status,
                reason=status.reason,
            )
            refund = await self._uow.refund_repository.insert(data=refund_obj)
            await self._uow.commit()
        refund_event = RefundCreatedEvent(
            refund_id=refund.id,
            user_id=payment.account_id,
            license_id=payment.subscription_id,
        )
        await self._handler.handle_refund_event(refund_event)
        return refund
