from http import HTTPStatus

from src.exceptions.base import BaseApplicationException


class WalletNotFoundException(BaseApplicationException):
    def __init__(self, message="Сведения о платежном способе не найдены"):
        self.code = HTTPStatus.NOT_FOUND
        self.message = message
