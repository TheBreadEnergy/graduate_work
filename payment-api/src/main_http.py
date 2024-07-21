from contextlib import asynccontextmanager

import uvicorn
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination
from redis.asyncio import Redis
from src import cache
from src.api import healthcheck
from src.api.v1 import event, payments, refunds, wallets
from src.cache import redis
from src.core.settings import settings
from src.dependencies.main import setup_dependencies
from src.exceptions.base import BaseApplicationException
from src.middlewares.main import setup_middleware
from src.producers import kafka
from starlette.responses import JSONResponse
from yookassa import Configuration


def create_application() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        redis.client = Redis(host=settings.cache_host, port=settings.cache_port)
        kafka.kafka_client = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_broker_host,
            retry_backoff_ms=settings.retry_backoff_ms,
        )
        Configuration.configure(
            account_id=settings.shop_url, secret_key=settings.shop_secret
        )
        await kafka.kafka_client.start()
        yield
        await cache.redis.client.close()
        await kafka.kafka_client.stop()

    app = FastAPI(
        title=settings.project_name,
        description=settings.description,
        docs_url="/api/payments/openapi",
        openapi_url="/api/payments/openapi.json",
        default_response_class=ORJSONResponse,
        version=settings.version,
        lifespan=lifespan,
    )

    @app.exception_handler(BaseApplicationException)
    def authjwt_exception_handler(_: Request, exc: BaseApplicationException):
        return JSONResponse(status_code=exc.code, content={"detail": exc.message})

    app.include_router(payments.router, prefix="/api/v1/payments")
    app.include_router(refunds.router, prefix="/api/v1/refunds")
    app.include_router(wallets.router, prefix="/api/v1/wallets")
    app.include_router(event.router, prefix="/api/v1/payment-events")
    app.include_router(healthcheck.router, tags=["Healthcheck"])
    setup_middleware(app)
    add_pagination(app)
    setup_dependencies(app)
    return app


app = create_application()

if __name__ == "__main__":
    uvicorn.run("main_http:app", host="0.0.0.0", port=8000)
