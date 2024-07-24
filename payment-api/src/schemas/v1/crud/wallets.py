import datetime
from uuid import UUID

from pydantic import BaseModel


class WalletSchema(BaseModel):
    id: UUID
    title: str
    account_id: UUID
    payment_method_id: UUID
    created: datetime.datetime
    preffered: bool | None


class WalletCreateSchema(BaseModel):
    title: str
    account_id: UUID
    reccurent_payment: bool = True
    payment_method_id: UUID


class WalletMakePrefferableSchema(BaseModel):
    preferrable: bool
