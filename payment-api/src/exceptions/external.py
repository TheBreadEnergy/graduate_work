from http import HTTPStatus

from src.exceptions.base import BaseApplicationException


class ExternalPaymentUnavailableException(BaseApplicationException):
    def __init__(self, message="External Payment gateway unavailable"):
        self.message = message
        self.code = HTTPStatus.BAD_GATEWAY


class ExternalServiceUnavailableException(BaseApplicationException):
    def __init__(self, message="External service unavailable"):
        self.message = message
        self.code = HTTPStatus.BAD_GATEWAY


class ExternalIpNotTrustedException(BaseApplicationException):
    def __init__(self, ip_address: str, message: str = "Посторонний внешний ip  адрес"):
        self.code = HTTPStatus.BAD_REQUEST
        self.message = f"{message}: {ip_address}"
