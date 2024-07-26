import uuid

from sqlalchemy import Boolean, Column, DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as UUIDType

from src.database.base import Base


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(UUIDType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUIDType(as_uuid=True), nullable=False, unique=True)
    subscription_id = Column(UUIDType(as_uuid=True))
    price = Column(Numeric, nullable=False)
    currency = Column(String(255), nullable=False)
    promo_id = Column(UUIDType(as_uuid=True), nullable=True)
    active = Column(Boolean, nullable=False)
    last_notified = Column(DateTime(timezone=True))
    last_payed = Column(DateTime(timezone=True))
