from pydantic import BaseModel


class PaymentEventRaw(BaseModel):
    type: str
    event: str
    object: dict
