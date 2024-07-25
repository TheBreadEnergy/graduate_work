import uuid

from sqlalchemy import DECIMAL, TEXT, Column, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID as UUIDType
from src.database.base import Base
from src.enums.payment import PaymentStatus


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(UUIDType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idempotency_key = Column(TEXT, nullable=True)
    payment_id = Column(UUIDType(as_uuid=True), nullable=False)
    description = Column(TEXT, nullable=True)
    account_id = Column(UUIDType(as_uuid=True), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.created, nullable=False)
    money = Column(DECIMAL, nullable=False)
    reason = Column(TEXT, nullable=True)
    created = Column(DateTime(timezone=True), nullable=False)
