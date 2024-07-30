from enum import Enum


class PaymentStatus(Enum):
    created = "created"
    pending = "pending"
    succeeded = "succeeded"
    cancelled = "cancelled"
    waiting_to_capture = "waiting_for_capture"
