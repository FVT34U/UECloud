from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    return JSONResponse(
        {
            "status": exc.status_code,
            "detail": exc.detail,
        }
    )