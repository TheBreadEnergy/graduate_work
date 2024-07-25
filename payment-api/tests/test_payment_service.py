import datetime
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from src.enums.payment import PaymentStatus
from src.exceptions.payment import PaymentNotFoundException
from src.models.domain.payment import Payment
from src.models.events.payment import PaymentCreatedEvent
from src.repositories.payment import PaymentRepositoryABC
from src.repositories.wallet import WalletRepositoryABC
from src.schemas.v1.billing.payments import (
    PayMethod,
    PaySchema,
    PayStatusSchema,
    ProductInformation,
)
from src.schemas.v1.crud.payments import PaymentCreateSchema
from src.schemas.v1.crud.wallets import WalletCreateSchema
from src.services.billing.payment_gateway import PaymentGatewayABC
from src.services.event_handler import EventHandlerABC
from src.services.payment import PaymentQueryService, PaymentService
from src.services.uow import UnitOfWorkABC


@pytest.mark.asyncio
async def test_get_payments():
    account_id = uuid.uuid4()
    mock_repository = MagicMock(spec=PaymentRepositoryABC)
    mock_repository.gets = AsyncMock()
    payment_query_service = PaymentQueryService(payment_repository=mock_repository)
    await payment_query_service.get_payments(account_id=account_id)
    mock_repository.gets.assert_awaited_once_with(account_id=account_id)


@pytest.mark.asyncio
async def test_success_get_payment():
    payment_id = uuid.uuid4()
    mock_repository = MagicMock(spec=PaymentRepositoryABC)
    mock_repository.get = AsyncMock(
        return_value=Payment(
            id=payment_id,
            account_id=payment_id,
            payment_id=payment_id,
            subscription_id=payment_id,
            price=Decimal(800),
            currency="RUB",
            status=PaymentStatus.success,
            idempotency_key=str(payment_id),
            description="",
            reason=None,
            created=datetime.datetime.now(datetime.timezone.utc),
        )
    )
    payment_query_service = PaymentQueryService(payment_repository=mock_repository)
    await payment_query_service.get_payment(payment_id=payment_id)
    mock_repository.get.assert_awaited_once_with(entity_id=payment_id)


@pytest.mark.asyncio
async def test_failure_get_payment():
    payment_id = uuid.uuid4()
    mock_repository = MagicMock(spec=PaymentRepositoryABC)
    mock_repository.get = AsyncMock(
        return_value=None,
    )
    payment_query_service = PaymentQueryService(payment_repository=mock_repository)
    with pytest.raises(PaymentNotFoundException):
        await payment_query_service.get_payment(payment_id=payment_id)
    mock_repository.get.assert_awaited_once_with(entity_id=payment_id)


@pytest.mark.asyncio
async def test_filter_payment():
    status = PaymentStatus.cancelled
    mock_repository = MagicMock(spec=PaymentRepositoryABC)
    mock_repository.filter_by_status = AsyncMock()
    payment_query_service = PaymentQueryService(payment_repository=mock_repository)
    await payment_query_service.filter_payments_by_status(status=status)
    mock_repository.filter_by_status.assert_awaited_once_with(status=status)


@pytest.mark.asyncio
async def test_payment_operation_with_save_payment_method():
    mock_id = uuid.uuid4()
    payment_gateway = MagicMock()
    payment_gateway.create_payment.return_value = PayStatusSchema(
        payment_id=mock_id,
        status=PaymentStatus.success,
        redirection_url="",
        reason=None,
        payment_information=PayMethod(title="Mock payment", payment_id=mock_id),
    )
    event_handler = MagicMock(spec=EventHandlerABC)
    event_handler.handle_payment_event = AsyncMock()
    uow = AsyncMock(spec=UnitOfWorkABC)
    uow.payment_repository = MagicMock(spec=PaymentRepositoryABC)
    uow.wallet_repository = MagicMock(spec=WalletRepositoryABC)
    uow.payment_repository.insert.return_value = Payment(
        id=mock_id,
        account_id=mock_id,
        payment_id=mock_id,
        subscription_id=mock_id,
        price=Decimal(800),
        currency="RUB",
        status=PaymentStatus.success,
        idempotency_key=str(mock_id),
        description="",
        reason=None,
        created=datetime.datetime.now(datetime.timezone.utc),
    )
    uow.wallet_repository.insert = AsyncMock()
    payment_service = PaymentService(
        payment_gateway=payment_gateway, event_hander=event_handler, uow=uow
    )
    await payment_service.make_payment(
        subscription_id=mock_id,
        subscription_name="test",
        price=Decimal(100),
        currency="RUB",
        account_id=mock_id,
        save_payment_method=True,
        payment_method="bank_card",
    )

    request = PaySchema(
        description="test",
        product_information=ProductInformation(
            product_id=mock_id,
            product_name="test",
            price=Decimal(100),
            currency="RUB",
        ),
        payment_method="bank_card",
        save_payment_method=True,
    )

    payment = PaymentCreateSchema(
        account_id=mock_id,
        description="test",
        payment_id=str(mock_id),
        subscription_id=mock_id,
        price=Decimal(100),
        currency="RUB",
        status=PaymentStatus.success,
        reason=None,
    )

    wallet = WalletCreateSchema(
        account_id=mock_id,
        payment_method_id=mock_id,
        title="Mock payment",
        reccurent_payment=True,
    )
    payment_gateway.create_payment.assert_called_once_with(
        payment_data=request, wallet_id=None, idempotency_key=str(mock_id)
    )
    uow.payment_repository.insert.assert_called_once_with(data=payment)
    uow.wallet_repository.insert.assert_called_once_with(data=wallet)
    payment_event = PaymentCreatedEvent(
        user_id=mock_id,
        license_id=payment.subscription_id,
        payment_id=mock_id,
    )
    event_handler.handle_payment_event.assert_awaited_once_with(payment_event)


@pytest.mark.asyncio
async def test_payment_operation_without_save_payment_method():
    mock_id = uuid.uuid4()
    payment_gateway = MagicMock()
    payment_gateway.create_payment.return_value = PayStatusSchema(
        payment_id=mock_id,
        status=PaymentStatus.success,
        redirection_url="",
        reason=None,
        payment_information=None,
    )
    event_handler = MagicMock(spec=EventHandlerABC)
    event_handler.handle_payment_event = AsyncMock()
    uow = AsyncMock(spec=UnitOfWorkABC)
    uow.payment_repository = MagicMock(spec=PaymentRepositoryABC)
    uow.wallet_repository = MagicMock(spec=WalletRepositoryABC)
    uow.payment_repository.insert.return_value = Payment(
        id=mock_id,
        account_id=mock_id,
        payment_id=mock_id,
        subscription_id=mock_id,
        price=Decimal(800),
        currency="RUB",
        status=PaymentStatus.success,
        idempotency_key=str(mock_id),
        description="",
        reason=None,
        created=datetime.datetime.now(datetime.timezone.utc),
    )
    uow.wallet_repository.insert = AsyncMock()
    payment_service = PaymentService(
        payment_gateway=payment_gateway, event_hander=event_handler, uow=uow
    )
    await payment_service.make_payment(
        subscription_id=mock_id,
        subscription_name="test",
        price=Decimal(100),
        currency="RUB",
        account_id=mock_id,
        save_payment_method=False,
        payment_method="bank_card",
    )

    request = PaySchema(
        description="test",
        product_information=ProductInformation(
            product_id=mock_id,
            product_name="test",
            price=Decimal(100),
            currency="RUB",
        ),
        payment_method="bank_card",
        save_payment_method=False,
    )

    payment = PaymentCreateSchema(
        account_id=mock_id,
        description="test",
        payment_id=str(mock_id),
        subscription_id=mock_id,
        price=Decimal(100),
        currency="RUB",
        status=PaymentStatus.success,
        reason=None,
    )
    payment_gateway.create_payment.assert_called_once_with(
        payment_data=request, wallet_id=None, idempotency_key=str(mock_id)
    )
    uow.payment_repository.insert.assert_called_once_with(data=payment)
    uow.wallet_repository.insert.assert_not_called()
    payment_event = PaymentCreatedEvent(
        user_id=mock_id,
        license_id=payment.subscription_id,
        payment_id=mock_id,
    )
    event_handler.handle_payment_event.assert_awaited_once_with(payment_event)


@pytest.mark.asyncio
async def test_payment_operation_without_save_payment_method_with_payment_data():
    mock_id = uuid.uuid4()
    payment_gateway = MagicMock(PaymentGatewayABC)
    payment_gateway.create_payment.return_value = PayStatusSchema(
        payment_id=mock_id,
        status=PaymentStatus.success,
        redirection_url="",
        reason=None,
        payment_information=PayMethod(title="Mock payment", payment_id=mock_id),
    )
    event_handler = MagicMock(spec=EventHandlerABC)
    event_handler.handle_payment_event = AsyncMock()
    uow = AsyncMock(spec=UnitOfWorkABC)
    uow.payment_repository = MagicMock(spec=PaymentRepositoryABC)
    uow.wallet_repository = MagicMock(spec=WalletRepositoryABC)
    uow.payment_repository.insert.return_value = Payment(
        id=mock_id,
        account_id=mock_id,
        payment_id=mock_id,
        subscription_id=mock_id,
        price=Decimal(800),
        currency="RUB",
        status=PaymentStatus.success,
        idempotency_key=str(mock_id),
        description="",
        reason=None,
        created=datetime.datetime.now(datetime.timezone.utc),
    )
    uow.wallet_repository.insert = AsyncMock()
    payment_service = PaymentService(
        payment_gateway=payment_gateway, event_hander=event_handler, uow=uow
    )
    await payment_service.make_payment(
        subscription_id=mock_id,
        subscription_name="test",
        price=Decimal(100),
        currency="RUB",
        account_id=mock_id,
        save_payment_method=False,
        payment_method="bank_card",
    )

    request = PaySchema(
        description="test",
        product_information=ProductInformation(
            product_id=mock_id,
            product_name="test",
            price=Decimal(100),
            currency="RUB",
        ),
        payment_method="bank_card",
        save_payment_method=False,
    )

    payment = PaymentCreateSchema(
        account_id=mock_id,
        description="test",
        payment_id=str(mock_id),
        subscription_id=mock_id,
        price=Decimal(100),
        currency="RUB",
        status=PaymentStatus.success,
        reason=None,
    )

    payment_gateway.create_payment.assert_called_once_with(
        payment_data=request, wallet_id=None, idempotency_key=str(mock_id)
    )
    uow.payment_repository.insert.assert_called_once_with(data=payment)
    uow.wallet_repository.insert.assert_not_called()
    payment_event = PaymentCreatedEvent(
        user_id=mock_id,
        license_id=payment.subscription_id,
        payment_id=mock_id,
    )
    event_handler.handle_payment_event.assert_awaited_once_with(payment_event)
