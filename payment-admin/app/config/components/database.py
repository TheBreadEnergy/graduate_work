import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST", "payment-admin-db"),
        "PORT": os.environ.get("DB_PORT", 5432),
        "OPTIONS": {"options": "-c search_path=public,content"},
    },
    "subscriptions": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("SUBSCRIPTIONS_DB_NAME", "subscriptions"),
        "USER": os.environ.get("SUBSCRIPTIONS_DB_USER", "db_user"),
        "PASSWORD": os.environ.get("SUBSCRIPTIONS_DB_PASSWORD", "wow-so-secret"),
        "HOST": os.environ.get("SUBSCRIPTIONS_DB_HOST", "subscription-db"),
        "PORT": os.environ.get("SUBSCRIPTIONS_DB_PORT", 5432),
        "OPTIONS": {"options": "-c search_path=public,content"},
    },
    "payments": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("PAYMENTS_DB_NAME", "payments"),
        "USER": os.environ.get("PAYMENTS_DB_USER", "db_user"),
        "PASSWORD": os.environ.get("PAYMENTS_DB_PASSWORD", "wow-so-secret"),
        "HOST": os.environ.get("PAYMENTS_DB_HOST", "payment-db"),
        "PORT": os.environ.get("PAYMENTS_DB_PORT", 5432),
        "OPTIONS": {"options": "-c search_path=public,content"},
    },
}


class DatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "billing":
            if model._meta.db_table in ["payments", "refunds", "wallets"]:
                return "payments"
            elif model._meta.db_table in ["subscriptions", "user_subscriptions"]:
                return "subscriptions"
        return "default"

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "billing":
            if model._meta.db_table in ["payments", "refunds", "wallets"]:
                return "payments"
            elif model._meta.db_table in ["subscriptions", "user_subscriptions"]:
                return "subscriptions"
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations for all models within the same app,
        and also for Permission and ContentType.
        """
        if obj1._meta.app_label == obj2._meta.app_label:
            return True

        # Allow Permission and ContentType relationship
        if (
            obj1._meta.app_label == "auth" and obj2._meta.app_label == "contenttypes"
        ) or (
            obj2._meta.app_label == "auth" and obj1._meta.app_label == "contenttypes"
        ):
            return True

        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "billing":
            if model_name in [
                "Payment",
                "Refund",
                "Wallet",
                "Subscription",
                "UserSubscription",
            ]:
                return False
        return True


DATABASE_ROUTERS = ["config.components.database.DatabaseRouter"]
