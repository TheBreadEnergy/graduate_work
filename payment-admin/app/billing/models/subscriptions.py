from billing.models.mixins import UUIDMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Subscription(UUIDMixin, models.Model):
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), null=True)
    tier = models.IntegerField(_("tier"))
    code = models.IntegerField(_("code"), unique=True)
    price = models.DecimalField(_("price"), max_digits=10, decimal_places=2)
    currency = models.CharField(_("currency"), max_length=255)
    created = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")

        db_table = "subscriptions"
        managed = False
        app_label = "billing"


class UserSubscription(UUIDMixin, models.Model):
    user_id = models.UUIDField(_("user id"), unique=True)
    subscription_id = models.UUIDField(_("subscription id"))
    price = models.DecimalField(_("price"), max_digits=10, decimal_places=2)
    currency = models.CharField(_("currency"), max_length=255)
    promo_id = models.UUIDField(_("promo id"), null=True)
    active = models.BooleanField(_("active"), default=True)
    last_notified = models.DateTimeField(_("last notified"), default=timezone.now)
    last_payed = models.DateTimeField(_("last payed"), default=timezone.now)
    created = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("User Subscription")
        verbose_name_plural = _("User Subscriptions")

        db_table = "user_subscriptions"
        managed = False
        app_label = "billing"
