from django.contrib import admin

from .models.user import User

# TODO: Add custom ModelAdmin for multiDB
# https://docs.djangoproject.com/en/5.0/topics/db/multi-db/#exposing-multiple-databases-in-django-s-admin-interface



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "login", "email")
    search_fields = ("id", "login", "email")
