import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from src.exceptions.refund import RefundNotFoundException
from src.models.domain.refund import Refund
from src.repositories.payment import PaymentRepositoryABC
from src.repositories.refunds import RefundRepositoryABC
from src.services.billing.payment_gateway import PaymentGatewayABC
from src.services.event_handler import EventHandlerABC
from src.services.refund import RefundQueryService, RefundService
from src.services.uow import UnitOfWorkABC
from tests.testdata.refund import REFUND, REFUND_DATASET, RefundTestData

pytestmark = pytest.mark.asyncio


async def test_gets_refund():
    # Arrange
    account_id = uuid.uuid4()

    mock_repository = MagicMock(spec=RefundRepositoryABC)
    mock_repository.gets = AsyncMock()

    refund_query_service = RefundQueryService(refund_repository=mock_repository)

    # Act
    await refund_query_service.get_refunds_for_account(account_id=account_id)

    # Assert
    mock_repository.gets.assert_awaited_once_with(account_id=account_id)


@pytest.mark.parametrize("refund", [REFUND])
async def test_success_get_refund(refund: Refund):

    # Arrange
    mock_repository = MagicMock(spec=RefundRepositoryABC)
    mock_repository.get = AsyncMock(return_value=refund)

    refund_query_service = RefundQueryService(refund_repository=mock_repository)

    # Act
    await refund_query_service.get_refund(refund_id=refund.id)

    # Assert
    mock_repository.get.assert_awaited_once_with(entity_id=refund.id)


async def test_failure_get_refund():

    # Arrange
    refund_id = uuid.uuid4()

    mock_repository = MagicMock(spec=RefundRepositoryABC)
    mock_repository.get = AsyncMock(return_value=None)

    refund_query_service = RefundQueryService(refund_repository=mock_repository)

    # Act + Assert
    with pytest.raises(RefundNotFoundException):
        await refund_query_service.get_refund(refund_id=refund_id)

    mock_repository.get.assert_awaited_once_with(entity_id=refund_id)


@pytest.mark.parametrize("refund_dataset", REFUND_DATASET)
async def test_refund_operation(refund_dataset: RefundTestData):
    # Arrange
    payment_gateway = MagicMock(spec=PaymentGatewayABC)
    payment_gateway.create_refund.return_value = refund_dataset.refund_status

    event_handler = MagicMock(spec=EventHandlerABC)
    event_handler.handle_refund_event = AsyncMock()

    uow = MagicMock(spec=UnitOfWorkABC)
    uow.refund_repository = MagicMock(spec=RefundRepositoryABC)
    uow.refund_repository.insert = AsyncMock(return_value=refund_dataset.refund)
    uow.payment_repository = MagicMock(spec=PaymentRepositoryABC)
    uow.payment_repository.get = AsyncMock(return_value=refund_dataset.payment)

    refund_service = RefundService(
        payment_gateway=payment_gateway, event_handler=event_handler, uow=uow
    )

    # Act
    await refund_service.refund(refund_dataset.payment.id)

    # Assert
    uow.payment_repository.get.assert_awaited_once_with(
        entity_id=refund_dataset.payment.id
    )
    payment_gateway.create_refund.assert_called_once_with(refund_dataset.payment)
    uow.refund_repository.insert.assert_awaited_once_with(
        data=refund_dataset.refund_create_schema
    )
    event_handler.handle_refund_event.assert_awaited_once_with(
        refund_dataset.refund_event
    )
