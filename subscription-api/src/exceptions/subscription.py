from http import HTTPStatus

from src.exceptions.base import BaseApplicationDomainException


class SubscriptionNotFoundException(BaseApplicationDomainException):
    def __init__(self, message: str = "Подписка не найдена"):
        super().__init__(code=HTTPStatus.NOT_FOUND, message=message)
