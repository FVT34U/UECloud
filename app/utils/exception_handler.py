from fastapi import HTTPException, Request, status
from fastapi.responses import RedirectResponse


async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        print("[LOG]: Got 401 status, redirecting to '/login'...")
        return RedirectResponse("/login", status_code=302)