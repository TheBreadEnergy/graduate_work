import asyncio
import logging

import grpc
from src.core.grpc.services import subscription_pb2_grpc
from src.core.settings import settings
from src.database.models import init_mappers
from src.services.grpc.subscriptions import GrpcUserSubscriptionManager


async def serve() -> None:
    logging.info("Server launching....")
    server = grpc.aio.server()
    init_mappers()
    try:
        logging.info("Building dependencies.....")
        subscription_pb2_grpc.add_SubscriptionManagerServicer_to_server(
            GrpcUserSubscriptionManager(), server
        )
        logging.info("Added active routes")
        server.add_insecure_port(f"[::]:{settings.grpc_port}")
        await server.start()
        logging.info("Server ready to receive requests...")
        await server.wait_for_termination()
    finally:
        await server.stop(grace=None)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
