from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("payment-admin/", admin.site.urls),
]
