import datetime
from uuid import UUID

from pydantic import BaseModel


class WalletSchema(BaseModel):
    id: UUID
    title: str
    account_id: UUID
    payment_method_id: UUID
    created_at: datetime.datetime


class WalletCreateSchema(BaseModel):
    title: str
    account_id: UUID
    payment_method_id: UUID
    created_at: datetime.datetime
