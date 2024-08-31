import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from app.utils.exception_handler import http_exception_handler
from app.utils.s3_connection import S3Client
from app.routers.main_router import router as MainRouter
from app.routers.auth_router import router as AuthRouter
from app.utils.mongodb_connection import _client


app = FastAPI()
app.mount("/api/static", StaticFiles(directory="frontend"), name="static")

app.include_router(MainRouter)
app.include_router(AuthRouter)
app.add_exception_handler(HTTPException, http_exception_handler)


def main():
    pass

if __name__ == '__main__':
    main()