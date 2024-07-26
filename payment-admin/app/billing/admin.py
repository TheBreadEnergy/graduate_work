from billing.models import (Payment, Refund, Subscription, UserSubscription,
                            Wallet)
from django.contrib import admin


@admin.register(Payment, site=admin.site)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "payment_id",
        "description",
        "account_id",
        "subscription_id",
        "price",
        "currency",
        "status",
        "reason",
        "created",
    )
    list_filter = ("status", "created")
    search_fields = ("payment_id", "description", "account_id", "subscription_id")

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(Refund, site=admin.site)
class RefundAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "payment_id",
        "description",
        "account_id",
        "status",
        "money",
        "reason",
        "created",
    )
    list_filter = ("status", "created")
    search_fields = ("payment_id", "description", "account_id")


@admin.register(Wallet, site=admin.site)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "account_id",
        "payment_method_id",
        "reccurent_payment",
        "title",
        "preffered",
        "created",
    )
    list_filter = ("reccurent_payment", "preffered", "created")
    search_fields = ("account_id", "payment_method_id", "title")


@admin.register(Subscription, site=admin.site)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "tier",
        "code",
        "price",
        "currency",
        "created",
    )
    list_filter = ("tier", "created")
    search_fields = ("name", "description", "code")


@admin.register(UserSubscription, site=admin.site)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_id",
        "subscription_id",
        "price",
        "currency",
        "promo_id",
        "active",
        "last_notified",
        "last_payed",
        "created",
    )
    list_filter = ("active", "created")
    search_fields = ("user_id", "subscription_id", "promo_id")
