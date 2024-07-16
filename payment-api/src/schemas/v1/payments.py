import decimal
from uuid import UUID

from pydantic import BaseModel
from src.models.domain.payment import PaymentStatus


class CustomerInformation(BaseModel):
    email: str


class PaymentMethod(BaseModel):
    title: str
    payment_id: UUID


class ProductInformation(BaseModel):
    product_id: UUID
    product_name: str
    price: decimal
    currency: str


class PaymentCreateSchema(BaseModel):
    price: decimal
    description: str
    product_information: ProductInformation
    customer_information: CustomerInformation
    payment_method: str
    save_payment_method: bool


class PaymentStatusSchema(BaseModel):
    status: PaymentStatus
    redirection_url: str | None
    reason: str | None
    payment_information: PaymentMethod | None = None
