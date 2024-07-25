from http import HTTPStatus

from src.exceptions.base import BaseApplicationException


class RefundNotFoundException(BaseApplicationException):
    def __init__(self, message="Возврат не найден"):
        self.message = message
        self.code = HTTPStatus.NOT_FOUND
