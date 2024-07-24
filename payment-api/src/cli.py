import asyncio
import logging
from enum import Enum

import typer
import uvicorn
from src.main_grpc import serve


class ServerMode(Enum):
    http = "http"
    grpc = "grpc"


cli = typer.Typer()


@cli.command()
def start_app():
    uvicorn.run("main_http:app", host="0.0.0.0", port=8001)


@cli.command()
def start_grpc():
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())


@cli.command()
def serve_app(
    mode: ServerMode = typer.Option(
        "http", help="Режим запуска сервера, по умолчанию http"
    )
):
    typer.echo(f"Running in {mode.value} mode")
    match mode:
        case ServerMode.http:
            start_app()
        case ServerMode.grpc:
            start_grpc()
