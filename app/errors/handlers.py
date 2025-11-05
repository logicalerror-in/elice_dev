from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.errors.exceptions import AppError


async def app_error_handler(_: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "detail": exc.detail},
    )


async def validation_error_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"code": 422, "detail": exc.errors()},
    )


async def integrity_error_handler(_: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={"code": 409, "detail": "Database integrity error"},
    )


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
