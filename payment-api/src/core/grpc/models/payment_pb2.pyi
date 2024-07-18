from typing import ClassVar as _ClassVar
from typing import Iterable as _Iterable
from typing import Mapping as _Mapping
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class SubscriptionPaymentRequest(_message.Message):
    __slots__ = (
        "subscription_id",
        "account_id",
        "wallet_id",
        "subscription_name",
        "price",
        "currency",
    )
    SUBSCRIPTION_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    WALLET_ID_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_NAME_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    subscription_id: str
    account_id: str
    wallet_id: str
    subscription_name: str
    price: float
    currency: str
    def __init__(
        self,
        subscription_id: _Optional[str] = ...,
        account_id: _Optional[str] = ...,
        wallet_id: _Optional[str] = ...,
        subscription_name: _Optional[str] = ...,
        price: _Optional[float] = ...,
        currency: _Optional[str] = ...,
    ) -> None: ...

class BatchSubscriptionPaymentRequest(_message.Message):
    __slots__ = ("requests",)
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[SubscriptionPaymentRequest]
    def __init__(
        self,
        requests: _Optional[
            _Iterable[_Union[SubscriptionPaymentRequest, _Mapping]]
        ] = ...,
    ) -> None: ...

class SubscriptionPaymentResponse(_message.Message):
    __slots__ = ("status", "redirection_url", "reason")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REDIRECTION_URL_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    status: str
    redirection_url: str
    reason: str
    def __init__(
        self,
        status: _Optional[str] = ...,
        redirection_url: _Optional[str] = ...,
        reason: _Optional[str] = ...,
    ) -> None: ...

class BatchSubscriptionPaymentResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, status: _Optional[_Iterable[str]] = ...) -> None: ...
