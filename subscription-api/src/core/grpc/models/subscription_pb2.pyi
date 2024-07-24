from typing import ClassVar as _ClassVar
from typing import Optional as _Optional

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message

DESCRIPTOR: _descriptor.FileDescriptor

class SubscriptionRequest(_message.Message):
    __slots__ = ("subscription_id",)
    SUBSCRIPTION_ID_FIELD_NUMBER: _ClassVar[int]
    subscription_id: str
    def __init__(self, subscription_id: _Optional[str] = ...) -> None: ...

class SubscriptionResponse(_message.Message):
    __slots__ = ("subscription_id", "subscription_name", "price", "currency")
    SUBSCRIPTION_ID_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_NAME_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    subscription_id: str
    subscription_name: str
    price: float
    currency: str
    def __init__(
        self,
        subscription_id: _Optional[str] = ...,
        subscription_name: _Optional[str] = ...,
        price: _Optional[float] = ...,
        currency: _Optional[str] = ...,
    ) -> None: ...
