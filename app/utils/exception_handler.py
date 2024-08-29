from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        #print(f"[LOG]: Got 401 status: {exc.detail}")
        #return RedirectResponse("/login", status_code=302)
        return JSONResponse({"status": "HTTP_401_UNAUTHORIZED",
                             "detail": exc.detail})