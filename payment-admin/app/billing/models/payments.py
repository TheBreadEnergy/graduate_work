from django.conf import settings
from django.db import models
import uuid


class PaymentStatus(models.TextChoices):
    CREATED = "created"
    PENDING = "pending"
    SUCCESS = "succeeded"
    CANCELLED = "cancelled"
    WAITING_TO_CAPTURE = "waiting_for_capture"


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_id = models.UUIDField()
    idempotency_key = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    currency = models.CharField(max_length=255)
    account_id = models.UUIDField()
    subscription_id = models.UUIDField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=255, choices=[(tag.value, tag.value) for tag in PaymentStatus]
    )
    reason = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"
        managed = False
        app_label = "billing"


class Refund(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idempotency_key = models.CharField(max_length=255, null=True)
    payment_id = models.UUIDField()
    description = models.TextField(null=True)
    account_id = models.UUIDField()
    status = models.CharField(
        max_length=255, choices=[(tag.value, tag.value) for tag in PaymentStatus]
    )
    money = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "refunds"
        managed = False
        app_label = "billing"


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_id = models.UUIDField()
    payment_method_id = models.UUIDField()
    reccurent_payment = models.BooleanField()
    title = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    preffered = models.BooleanField(null=True)

    class Meta:
        db_table = "wallets"
        managed = False
        app_label = "billing"
