from uuid import uuid4

from django.db import models
from django.utils import timezone


class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    tier = models.IntegerField()
    code = models.IntegerField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "subscriptions"
        managed = False
        app_label = "billing"


class UserSubscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user_id = models.UUIDField(unique=True)
    subscription_id = models.UUIDField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=255)
    promo_id = models.UUIDField(null=True)
    active = models.BooleanField(default=True)
    last_notified = models.DateTimeField(default=timezone.now)
    last_payed = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_subscriptions"
        managed = False
        app_label = "billing"
