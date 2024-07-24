from http import HTTPStatus

from src.exceptions.base import BaseApplicationDomainException


class UserSubscriptionNotFoundException(BaseApplicationDomainException):
    def __init__(self, message="Данной подписки у пользователя не обнаружено"):
        self.code = HTTPStatus.NOT_FOUND
        self.message = message
