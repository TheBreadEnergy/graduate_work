import datetime
import uuid

import sqlalchemy
from sqlalchemy import Column, Table
from sqlalchemy.orm import registry, relationship
from src.models.domain.subscription import Subscription
from src.models.domain.user_subscription import UserSubscription

mapper_registry = registry()


def date_factory():
    return datetime.datetime.now(datetime.timezone.utc)


subscription_table = Table(
    "subscriptions",
    mapper_registry.metadata,
    Column("id", sqlalchemy.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("name", sqlalchemy.TEXT, nullable=False),
    Column("description", sqlalchemy.TEXT, nullable=True),
    Column("tier", sqlalchemy.INTEGER, nullable=False),
    Column("code", sqlalchemy.INTEGER, nullable=False, autoincrement=True),
    Column("price", sqlalchemy.DECIMAL, nullable=False),
    Column("currency", sqlalchemy.String(length=255), nullable=False),
    Column(
        "created",
        sqlalchemy.DateTime(timezone=True),
        default=date_factory,
    ),
)

user_subscription_table = Table(
    "user_subscriptions",
    mapper_registry.metadata,
    Column("id", sqlalchemy.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column(
        "user_id",
        sqlalchemy.UUID(as_uuid=True),
        nullable=False,
        index=True,
        unique=True,
    ),
    Column(
        "subscription_id",
        sqlalchemy.UUID(as_uuid=True),
        sqlalchemy.ForeignKey("subscriptions.id", ondelete="CASCADE"),
    ),
    Column("price", sqlalchemy.DECIMAL, nullable=False),
    Column("currency", sqlalchemy.String(length=255), nullable=False),
    Column("promo_id", sqlalchemy.UUID(as_uuid=True), nullable=True),
    Column("active", sqlalchemy.BOOLEAN, nullable=False),
    Column("last_notified", sqlalchemy.DateTime(timezone=True), default=date_factory),
    Column("last_payed", sqlalchemy.DateTime(timezone=True), default=date_factory),
    Column(
        "created",
        sqlalchemy.DateTime(timezone=True),
        nullable=True,
        default=date_factory,
    ),
)


def init_mappers():
    subscription_mapper = mapper_registry.map_imperatively(
        Subscription, subscription_table
    )

    mapper_registry.map_imperatively(
        UserSubscription,
        user_subscription_table,
        properties={
            "subscription": relationship(
                subscription_mapper,
                lazy="selectin",
                cascade="all, delete-orphan",
                single_parent=True,
                uselist=False,
            ),
        },
    )
