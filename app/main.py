import asyncio

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.utils.s3_connection import S3Client
from app.routers.main_router import router

app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend"), name="static")

app.include_router(router)

def main():
    pass

if __name__ == '__main__':
    main()