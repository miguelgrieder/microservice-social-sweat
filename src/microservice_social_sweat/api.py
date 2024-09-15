from typing import List, Union

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from microservice_social_sweat.services.generic_service.router import router as generic_router


class ErrorMessage(BaseModel):
    msg: str


class ErrorResponse(BaseModel):
    detail: Union[List[ErrorMessage], None]


router = APIRouter(
    default_response_class=JSONResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)


# Adiciona routers
router.include_router(generic_router, prefix="/generic", tags=["generic"])
