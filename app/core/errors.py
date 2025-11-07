from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


def standard_error(
    code: int, message: str, details: dict | None = None
) -> JSONResponse:
    content = {"error": {"code": code, "message": message}}
    if details:
        content["error"]["details"] = details
    return JSONResponse(status_code=code, content=content)


async def http_exception_handler(_: Request, exc: HTTPException):
    return standard_error(exc.status_code, exc.detail)


async def validation_error_handler(_: Request, exc: RequestValidationError):
    return standard_error(422, "Validation error", exc.errors())


async def integrity_error_handler(_: Request, exc: IntegrityError):
    return standard_error(409, "Conflict")


def register_handlers(app):
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)