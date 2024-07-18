import uuid

import sqlalchemy
from sqlalchemy import Column, Table
from sqlalchemy.orm import registry
from src.models.domain.payment import Payment, PaymentStatus
from src.models.domain.refund import Refund
from src.models.domain.wallet import Wallet

mapper_registry = registry()

payments_table = Table(
    "payments",
    mapper_registry.metadata,
    Column("id", sqlalchemy.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("idempotency_key", sqlalchemy.TEXT, nullable=True),
    Column("description", sqlalchemy.TEXT, nullable=True),
    Column("account_id", sqlalchemy.UUID(as_uuid=True), nullable=False),
    Column("subscription_id", sqlalchemy.UUID(as_uuid=True), nullable=False),
    Column("price", sqlalchemy.DECIMAL, nullable=False),
    Column(
        "status",
        sqlalchemy.Enum(PaymentStatus),
        default=PaymentStatus.created,
        nullable=False,
    ),
    Column("reason", sqlalchemy.TEXT, nullable=True),
    Column("created", sqlalchemy.DateTime(timezone=True), nullable=False),
)

refunds_table = Table(
    "refunds",
    mapper_registry.metadata,
    Column("id", sqlalchemy.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("idempotency_key", sqlalchemy.TEXT, nullable=True),
    Column("payment_id", sqlalchemy.UUID(as_uuid=True), nullable=False),
    Column("description", sqlalchemy.TEXT, nullable=True),
    Column("account_id", sqlalchemy.UUID(as_uuid=True), nullable=False),
    Column(
        "status",
        sqlalchemy.Enum(PaymentStatus),
        default=PaymentStatus.created,
        nullable=False,
    ),
    Column("money", sqlalchemy.DECIMAL, nullable=False),
    Column("reason", sqlalchemy.TEXT, nullable=True),
    Column("created", sqlalchemy.DateTime(timezone=True), nullable=False),
)

wallets_table = Table(
    "wallets",
    mapper_registry.metadata,
    Column("id", sqlalchemy.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("account_id", sqlalchemy.UUID(as_uuid=True), nullable=False),
    Column("payment_method_id", sqlalchemy.UUID(as_uuid=True), nullable=False),
    Column("reccurent_payment", sqlalchemy.Boolean),
    Column("title", sqlalchemy.TEXT),
    Column("created", sqlalchemy.DateTime(timezone=True), nullable=False),
)


def init_mappers():
    mapper_registry.map_imperatively(Payment, payments_table)
    mapper_registry.map_imperatively(Refund, refunds_table)
    mapper_registry.map_imperatively(Wallet, wallets_table)
