from contextlib import asynccontextmanager
from http import HTTPStatus

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis
from src import cache
from src.api import healthcheck
from src.api.v1 import subscriptions, user_subscriptions
from src.cache import redis
from src.core.settings import settings
from src.core.tracing import configure_tracing
from src.database.models import init_mappers
from src.dependencies.main import setup_dependencies
from src.exceptions.base import BaseApplicationDomainException
from src.middlewares.main import setup_middleware
from starlette.responses import JSONResponse


def create_application() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        init_mappers()
        redis.client = Redis(host=settings.cache_host, port=settings.cache_port)
        yield
        await cache.redis.client.close()

    app = FastAPI(
        title=settings.project_name,
        description=settings.description,
        docs_url="/api/subscriptions/openapi",
        openapi_url="/api/subscriptions/openapi.json",
        default_response_class=ORJSONResponse,
        version=settings.version,
        lifespan=lifespan,
    )

    if settings.enable_tracer:
        configure_tracing()

        @app.middleware("http")
        async def before_request(request: Request, call_next):
            response = await call_next(request)
            request_id = request.headers.get("X-Request-Id")
            if not request_id:
                return ORJSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"detail": "X-Request-Id is required"},
                )
            return response

        FastAPIInstrumentor.instrument_app(app)

    @app.exception_handler(BaseApplicationDomainException)
    def exception_handler(_: Request, exc: BaseApplicationDomainException):
        return JSONResponse(status_code=exc.code, content={"detail": str(exc.message)})

    app.include_router(subscriptions.router, prefix="/api/v1/subscriptions")
    app.include_router(user_subscriptions.router, prefix="/api/v1/user-subscriptions")
    app.include_router(healthcheck.router, tags=["Healthcheck"])
    setup_middleware(app)
    add_pagination(app)
    setup_dependencies(app)
    return app


app = create_application()

if __name__ == "__main__":
    uvicorn.run("main_http:app", host="0.0.0.0", port=8000)
