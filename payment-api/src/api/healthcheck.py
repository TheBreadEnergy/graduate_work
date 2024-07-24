from http import HTTPStatus

from fastapi import APIRouter

router = APIRouter()


@router.get("/healthcheck", description="Perform healthcheck of service")
async def healthcheck():
    return HTTPStatus.OK
