import decimal
from uuid import UUID

from pydantic import BaseModel
from src.enums.payment import PaymentStatus


class PayMethod(BaseModel):
    title: str
    payment_id: UUID


class ProductInformation(BaseModel):
    product_id: UUID
    product_name: str
    price: decimal.Decimal
    currency: str


class PaySchema(BaseModel):
    description: str
    product_information: ProductInformation
    payment_method: str | None
    save_payment_method: bool


class PayStatusSchema(BaseModel):
    status: PaymentStatus
    redirection_url: str | None
    payment_information: PayMethod | None = None
    reason: str | None
