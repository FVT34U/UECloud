from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return JSONResponse(
            {
                "status": "HTTP_401_UNAUTHORIZED",
                "detail": exc.detail,
            }
        )
    elif exc.status_code == status.HTTP_404_NOT_FOUND:
        return JSONResponse(
            {
                "status": "HTTP_404_NOT_FOUND",
                "detail": exc.detail,
            }
        )