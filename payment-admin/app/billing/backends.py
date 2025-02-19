import http
import json

import backoff
import requests
from billing.models.user import Roles
from circuitbreaker import circuit
from config import settings
from config.settings import BACKOFF_CONFIG, CIRCUIT_CONFIG
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from requests import RequestException

User = get_user_model()


class CustomBackend(BaseBackend):
    @backoff.on_exception(**BACKOFF_CONFIG)
    @circuit(**CIRCUIT_CONFIG)
    def authenticate(self, request, username=None, password=None):
        auth_url = settings.AUTH_API_LOGIN_URL
        profile_url = settings.AUTH_API_PROFILE_URL
        ssl_cert = settings.SSL_CERT_PATH
        payload = {"login": username, "password": password}
        response = requests.post(
            auth_url,
            data=json.dumps(payload),
            verify=ssl_cert,
        )
        print(response.status_code)
        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()
        token = data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            profile_url,
            headers=headers,
            verify=ssl_cert,
        )
        if response.status_code != http.HTTPStatus.OK:
            return None
        data = response.json()
        try:
            user, created = User.objects.get_or_create(
                id=data["id"],
            )
            user.login = data.get("login")
            user.email = data.get("email")
            user.first_name = data.get("first_name")
            user.last_name = data.get("last_name")
            user.is_admin = any(
                [
                    (item.get("name") == Roles.ADMIN)
                    or (item.get("name") == Roles.SUPER_ADMIN)
                    for item in data.get("roles")
                ]
            )
            user.is_active = True
            user.save()
        except RequestException:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
