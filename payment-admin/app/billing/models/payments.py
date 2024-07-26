from billing.models.mixins import UUIDMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentStatus(models.TextChoices):
    CREATED = "created", _("created")
    PENDING = "pending", _("pending")
    SUCCESS = "succeeded", _("succeeded")
    CANCELLED = "cancelled", _("cancelled")
    WAITING_TO_CAPTURE = "waiting_for_capture", _("waiting_for_capture")


class Payment(UUIDMixin, models.Model):
    payment_id = models.UUIDField(_("payment id"))
    idempotency_key = models.CharField(max_length=255, null=True)
    description = models.TextField(_("description"), null=True)
    currency = models.CharField(_("currency"), max_length=255)
    account_id = models.UUIDField(_("account id"))
    subscription_id = models.UUIDField(_("subscription id"))
    price = models.DecimalField(
        _("price"),
        max_digits=10,
        decimal_places=2,
    )
    status = models.CharField(
        _("status"),
        max_length=255,
        choices=[(tag.value, tag.value) for tag in PaymentStatus],
    )
    reason = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")

        db_table = "payments"
        managed = False
        app_label = "billing"


class Refund(UUIDMixin, models.Model):
    idempotency_key = models.CharField(max_length=255, null=True)
    payment_id = models.UUIDField(_("payment id"))
    description = models.TextField(_("description"), null=True)
    account_id = models.UUIDField(_("account id"))
    status = models.CharField(
        _("status"),
        max_length=255,
        choices=[(tag.value, tag.value) for tag in PaymentStatus],
    )
    money = models.DecimalField(_("money"), max_digits=10, decimal_places=2)
    reason = models.TextField(_("reason"), null=True)
    created = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Refund")
        verbose_name_plural = _("Refunds")

        db_table = "refunds"
        managed = False
        app_label = "billing"


class Wallet(UUIDMixin, models.Model):
    account_id = models.UUIDField(_("account id"))
    payment_method_id = models.UUIDField(_("payment method id"))
    reccurent_payment = models.BooleanField(_("reccurent payment"))
    title = models.TextField(_("title"))
    created = models.DateTimeField(_("created"), auto_now_add=True)
    preffered = models.BooleanField(_("preffered"), null=True)

    class Meta:
        verbose_name = _("Wallet")
        verbose_name_plural = _("Wallets")

        db_table = "wallets"
        managed = False
        app_label = "billing"
