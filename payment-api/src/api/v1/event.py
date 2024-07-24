from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from src.schemas.v1.billing.events import EventSchema
from src.services.billing.event_processor import BillingEventProcessorABC

router = APIRouter()


@router.post(
    "/",
    description="Ручка для платежной системы для отправления событий об изменениях платежа",
    summary="Ручка для платежной системы для отправления событий об изменениях платежа",
    tags=["Платежная система"],
)
async def handle_events(
    event: EventSchema,
    request: Request,
    event_processor: BillingEventProcessorABC = Depends(),
):
    await event_processor.process_event(event, ip_address=request.client.host)
    return HTTPStatus.OK
