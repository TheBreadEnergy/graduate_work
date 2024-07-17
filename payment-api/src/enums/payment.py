from enum import Enum


class PaymentStatus(Enum):
    created = "created"
    pending = "pending"
    success = "succeeded"
    cancelled = "cancelled"
    waiting_to_capture = "waiting_for_capture"
