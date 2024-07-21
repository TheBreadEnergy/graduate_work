import asyncio
import logging

import grpc.aio
from src.core.grpc.services import payment_pb2_grpc
from src.core.settings import settings
from src.services.billing.payment_gateway import YooKassaPaymentGateway
from src.services.grpc.payment import GrpcPaymentService


async def serve() -> None:
    logging.info("Server launching....")
    server = grpc.aio.server()
    try:
        logging.info("Building dependencies.....")
        payment_pb2_grpc.add_PaymentManagerServicer_to_server(
            GrpcPaymentService(YooKassaPaymentGateway()), server
        )
        logging.info("Added active routes")
        server.add_insecure_port(f"[::]:{settings.grpc_port}")
        await server.start()
        logging.info("Server ready to receive requests...")
        await server.wait_for_termination()
    finally:
        await server.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
