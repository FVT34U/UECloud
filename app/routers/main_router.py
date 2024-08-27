from pathlib import Path
from typing import Annotated
from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from app.utils.s3_connection import S3Client


router = APIRouter()
client = S3Client("xxx", "xxx", "xxx", "xxx")


@router.get("/", response_class=HTMLResponse)
async def post_index():
    index_path = Path("frontend/index.html")
    return index_path.read_text(encoding="utf-8")


@router.post("/upload")
async def post_upload(path: Annotated[str, Form()]):
    await client.upload_file(path)


@router.post("/download")
async def post_download(path: Annotated[str, Form()]):
    await client.download_file(path)


@router.post("/delete")
async def post_delete(path: Annotated[str, Form()]):
    await client.delete_file(path)