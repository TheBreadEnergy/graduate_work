import uuid

from sqlalchemy import DECIMAL, TEXT, Column, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID as UUIDType

from src.database.base import Base
from src.enums.payment import PaymentStatus


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUIDType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(UUIDType(as_uuid=True), nullable=True)
    idempotency_key = Column(TEXT, nullable=True)
    description = Column(TEXT, nullable=True)
    currency = Column(TEXT, nullable=True)
    account_id = Column(UUIDType(as_uuid=True), nullable=False)
    subscription_id = Column(UUIDType(as_uuid=True), nullable=False)
    price = Column(DECIMAL, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.created, nullable=False)
    reason = Column(TEXT, nullable=True)
    created = Column(DateTime(timezone=True), nullable=False)
