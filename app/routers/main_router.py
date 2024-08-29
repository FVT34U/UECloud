from pathlib import Path
from typing import Annotated
from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from app.models.user import User, get_current_active_user
from app.utils.s3_connection import S3Client


router = APIRouter()
s3_client = S3Client(
    "L201GGN3PARM2UOEH46F",
    "Qk1rldX0xI3nPgncA8awr7DYAIjqA1jezkYf2rIo",
    "http://91.222.131.165:8080",
    "uecloud",
)


@router.get("/", response_class=HTMLResponse)
async def get_index(current_user: Annotated[User, Depends(get_current_active_user)]):
    index_path = Path("frontend/index.html")
    return index_path.read_text(encoding="utf-8")


@router.post("/upload")
async def post_upload(
    path: Annotated[str, Form()],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    await s3_client.upload_file(path)


@router.post("/download")
async def post_download(
    path: Annotated[str, Form()],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    await s3_client.download_file(path)


@router.post("/delete")
async def post_delete(
    path: Annotated[str, Form()],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    await s3_client.delete_file(path)


@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user