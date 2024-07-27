import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from src.enums.payment import PaymentStatus
from src.exceptions.payment import PaymentNotFoundException
from src.models.domain.payment import Payment
from src.repositories.payment import PaymentRepositoryABC
from src.repositories.wallet import WalletRepositoryABC
from src.services.event_handler import EventHandlerABC
from src.services.payment import PaymentQueryService, PaymentService
from src.services.uow import UnitOfWorkABC
from tests.testdata.payment import (
    DATASET_WITH_SAVE_METHOD,
    DATASET_WITHOUT_SAVE_METHOD,
    PAYMENT,
    PaymentTestData,
)

pytestmark = pytest.mark.asyncio


async def test_get_payments():

    # Arrange
    account_id = uuid.uuid4()
    mock_repository = MagicMock(spec=PaymentRepositoryABC)
    mock_repository.gets = AsyncMock()
    payment_query_service = PaymentQueryService(payment_repository=mock_repository)

    # Act
    await payment_query_service.get_payments(account_id=account_id)

    # Assert
    mock_repository.gets.assert_awaited_once_with(account_id=account_id)


@pytest.mark.parametrize("payment", [PAYMENT])
async def test_success_get_payment(payment: Payment):

    # Arrange
    mock_repository = MagicMock(spec=PaymentRepositoryABC)
    mock_repository.get = AsyncMock(return_value=payment)
    payment_query_service = PaymentQueryService(payment_repository=mock_repository)

    # Act
    await payment_query_service.get_payment(payment_id=payment.id)

    # Assert
    mock_repository.get.assert_awaited_once_with(entity_id=payment.id)


async def test_failure_get_payment():

    # Arrange
    payment_id = uuid.uuid4()
    mock_repository = MagicMock(spec=PaymentRepositoryABC)
    mock_repository.get = AsyncMock(return_value=None)
    payment_query_service = PaymentQueryService(payment_repository=mock_repository)

    # Act
    with pytest.raises(PaymentNotFoundException):
        await payment_query_service.get_payment(payment_id=payment_id)

    # Assert
    mock_repository.get.assert_awaited_once_with(entity_id=payment_id)


async def test_filter_payment():

    # Arrange
    status = PaymentStatus.cancelled
    mock_repository = MagicMock(spec=PaymentRepositoryABC)
    mock_repository.filter_by_status = AsyncMock()
    payment_query_service = PaymentQueryService(payment_repository=mock_repository)

    # Act
    await payment_query_service.filter_payments_by_status(status=status)

    # Assert
    mock_repository.filter_by_status.assert_awaited_once_with(status=status)


@pytest.mark.parametrize("payment_dataset", DATASET_WITH_SAVE_METHOD)
async def test_payment_operation_with_save_payment_method(
    payment_dataset: PaymentTestData,
):
    # Arrange
    payment_gateway = MagicMock()
    payment_gateway.create_payment.return_value = payment_dataset.pay_status

    uow = AsyncMock(spec=UnitOfWorkABC)
    uow.wallet_repository = MagicMock(spec=WalletRepositoryABC)
    uow.wallet_repository.insert = AsyncMock()
    uow.payment_repository = MagicMock(spec=PaymentRepositoryABC)
    uow.payment_repository.insert.return_value = payment_dataset.payment

    event_handler = MagicMock(spec=EventHandlerABC)
    event_handler.handle_payment_event = AsyncMock()
    payment_service = PaymentService(
        payment_gateway=payment_gateway, event_hander=event_handler, uow=uow
    )

    # Act
    await payment_service.make_payment(
        subscription_id=payment_dataset.payment.id,
        subscription_name=str(payment_dataset.payment.subscription_id),
        price=payment_dataset.payment.price,
        currency=payment_dataset.payment.currency,
        account_id=payment_dataset.payment.account_id,
        save_payment_method=True,
        payment_method="bank_card",
    )

    # Assert
    payment_gateway.create_payment.assert_called_once_with(
        payment_data=payment_dataset.pay_schema,
        wallet_id=None,
        idempotency_key=str(payment_dataset.payment.id),
    )
    uow.payment_repository.insert.assert_called_once_with(
        data=payment_dataset.payment_create_schema
    )
    uow.wallet_repository.insert.assert_called_once_with(data=payment_dataset.wallet)
    event_handler.handle_payment_event.assert_awaited_once_with(
        payment_dataset.payment_event
    )


@pytest.mark.parametrize("payment_dataset", [*DATASET_WITHOUT_SAVE_METHOD])
async def test_payment_operation_without_save_payment_method(
    payment_dataset: PaymentTestData,
):
    # Arrange
    payment_gateway = MagicMock()
    payment_gateway.create_payment.return_value = payment_dataset.pay_status

    event_handler = MagicMock(spec=EventHandlerABC)
    event_handler.handle_payment_event = AsyncMock()

    uow = AsyncMock(spec=UnitOfWorkABC)
    uow.payment_repository = MagicMock(spec=PaymentRepositoryABC)
    uow.wallet_repository = MagicMock(spec=WalletRepositoryABC)
    uow.payment_repository.insert.return_value = payment_dataset.payment
    uow.wallet_repository.insert = AsyncMock()

    payment_service = PaymentService(
        payment_gateway=payment_gateway, event_hander=event_handler, uow=uow
    )

    # Act
    await payment_service.make_payment(
        subscription_id=payment_dataset.payment.id,
        subscription_name=str(payment_dataset.payment.subscription_id),
        price=payment_dataset.payment.price,
        currency=payment_dataset.payment.currency,
        account_id=payment_dataset.payment.account_id,
        save_payment_method=False,
        payment_method="bank_card",
    )

    # Assert
    payment_gateway.create_payment.assert_called_once_with(
        payment_data=payment_dataset.pay_schema,
        wallet_id=None,
        idempotency_key=str(payment_dataset.payment.id),
    )
    uow.payment_repository.insert.assert_called_once_with(
        data=payment_dataset.payment_create_schema
    )
    uow.wallet_repository.insert.assert_not_called()
    event_handler.handle_payment_event.assert_awaited_once_with(
        payment_dataset.payment_event
    )
