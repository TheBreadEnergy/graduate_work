class BaseApplicationException(Exception):
    message: str
    code: int
