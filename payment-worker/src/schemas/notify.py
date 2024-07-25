from uuid import UUID

from pydantic import BaseModel


class NotifyMessage(BaseModel):
    id: UUID
    payment_id: UUID
    account_id: UUID
