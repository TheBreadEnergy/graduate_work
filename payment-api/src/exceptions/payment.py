from http import HTTPStatus

from src.exceptions.base import BaseApplicationException


class PaymentNotFoundException(BaseApplicationException):
    def __init__(self, message="Платеж не найден"):
        self.message = message
        self.code = HTTPStatus.NOT_FOUND
