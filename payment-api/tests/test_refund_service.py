import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from src.enums.payment import PaymentStatus
from src.exceptions.refund import RefundNotFoundException
from src.models.domain.payment import Payment
from src.models.domain.refund import Refund
from src.models.events.refund import RefundCreatedEvent
from src.repositories.payment import PaymentRepositoryABC
from src.repositories.refunds import RefundRepositoryABC
from src.schemas.v1.billing.refunds import RefundStatusSchema
from src.schemas.v1.crud.refunds import RefundCreateSchema
from src.services.billing.payment_gateway import PaymentGatewayABC
from src.services.event_handler import EventHandlerABC
from src.services.refund import RefundQueryService, RefundService
from src.services.uow import UnitOfWorkABC


@pytest.mark.asyncio
async def test_gets_refund():
    account_id = uuid.uuid4()
    mock_repository = MagicMock(spec=RefundRepositoryABC)
    mock_repository.gets = AsyncMock()
    refund_query_service = RefundQueryService(refund_repository=mock_repository)
    await refund_query_service.gets(account_id=account_id)
    mock_repository.gets.assert_awaited_once_with(account_id=account_id)


@pytest.mark.asyncio
async def test_success_get_refund():
    refund_id = uuid.uuid4()
    refund = Refund(
        account_id=refund_id,
        payment_id=refund_id,
        money=Decimal(100),
        status=PaymentStatus.success,
        reason=None,
        id=refund_id,
    )
    mock_repository = MagicMock(spec=RefundRepositoryABC)
    mock_repository.get = AsyncMock(return_value=refund)
    refund_query_service = RefundQueryService(refund_repository=mock_repository)
    await refund_query_service.get(refund_id=refund_id)
    mock_repository.get.assert_awaited_once_with(entity_id=refund_id)


@pytest.mark.asyncio
async def test_failure_get_refund():
    refund_id = uuid.uuid4()
    mock_repository = MagicMock(spec=RefundRepositoryABC)
    mock_repository.get = AsyncMock(return_value=None)
    refund_query_service = RefundQueryService(refund_repository=mock_repository)
    with pytest.raises(RefundNotFoundException):
        await refund_query_service.get(refund_id=refund_id)
    mock_repository.get.assert_awaited_once_with(entity_id=refund_id)


@pytest.mark.asyncio
async def test_refund_operation():
    mock_id = uuid.uuid4()
    payment_gateway = MagicMock(spec=PaymentGatewayABC)
    payment_gateway.create_refund.return_value = RefundStatusSchema(
        status=PaymentStatus.success, payment_id=mock_id, reason=None
    )
    event_handler = MagicMock(spec=EventHandlerABC)
    event_handler.handle_refund_event = AsyncMock()
    uow = MagicMock(spec=UnitOfWorkABC)
    uow.refund_repository = MagicMock(spec=RefundRepositoryABC)
    uow.refund_repository.insert = AsyncMock(
        return_value=Refund(
            account_id=mock_id,
            payment_id=mock_id,
            money=Decimal(100),
            status=PaymentStatus.success,
            id=mock_id,
        )
    )
    payment = Payment(
        id=mock_id,
        account_id=mock_id,
        payment_id=mock_id,
        subscription_id=mock_id,
        price=Decimal(100),
        currency="RUB",
        status=PaymentStatus.success,
        idempotency_key=str(mock_id),
        description="",
        reason=None,
    )
    uow.payment_repository = MagicMock(spec=PaymentRepositoryABC)
    uow.payment_repository.get = AsyncMock(return_value=payment)

    refund_obj = RefundCreateSchema(
        account_id=mock_id,
        payment_id=mock_id,
        description="",
        money=Decimal(100),
        status=PaymentStatus.success,
        reason=None,
    )
    refund_event = RefundCreatedEvent(
        refund_id=mock_id,
        user_id=mock_id,
        license_id=mock_id,
    )
    refund_service = RefundService(
        payment_gateway=payment_gateway, event_handler=event_handler, uow=uow
    )
    await refund_service.refund(mock_id)
    uow.payment_repository.get.assert_awaited_once_with(entity_id=mock_id)
    payment_gateway.create_refund.assert_called_once_with(payment)
    uow.refund_repository.insert.assert_awaited_once_with(data=refund_obj)
    event_handler.handle_refund_event.assert_awaited_once_with(refund_event)
