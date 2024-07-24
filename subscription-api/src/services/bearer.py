from functools import wraps
from http import HTTPStatus

import backoff
from aiohttp import ClientSession
from circuitbreaker import CircuitBreakerError, circuit
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.core.settings import BACKOFF_CONFIG, CIRCUIT_CONFIG, settings
from src.exceptions.rate_limit import RateLimitException
from src.schemas.token import TokenPayload
from src.schemas.user import UserDto


@backoff.on_exception(**BACKOFF_CONFIG)
@circuit(**CIRCUIT_CONFIG)
async def get_user_info(token: str) -> UserDto:
    token_payload = TokenPayload(access_token=token).model_dump(mode="json")
    async with ClientSession(trust_env=settings.trust_env) as session:
        response = await session.post(
            url=f"{settings.profile_endpoint}",
            json=token_payload,
            ssl=not settings.trust_env,
            headers={"Content-Type": "application/json"},
        )
        if response.status == HTTPStatus.TOO_MANY_REQUESTS:
            raise RateLimitException()
        if response.status != HTTPStatus.OK:
            raise HTTPException(status_code=response.status, detail=response.reason)
        body = await response.json()
        return UserDto(**body)


class JwtBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> UserDto:
        try:
            credentials: HTTPAuthorizationCredentials = await super().__call__(request)
            if not credentials:
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN,
                    detail="Invalid authorization code.",
                )
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail="Only Bearer token might be accepted",
                )
            return await self.get_user(token=credentials.credentials)
        except CircuitBreakerError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="Service unavailable"
            )

    @staticmethod
    async def get_user(token: str) -> UserDto:
        return await get_user_info(token=token)


security_jwt = JwtBearer()


def require_roles(roles: list[str]):
    def auth_decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs["user"]
            if not user:
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED, detail="Unauthorized"
                )
            for role in user.roles:
                if role.name in roles:
                    return await func(*args, **kwargs)
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="User have not access"
            )

        return wrapper

    return auth_decorator
