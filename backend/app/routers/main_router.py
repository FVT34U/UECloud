import os
from pathlib import Path
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, UploadFile,  status
from fastapi.responses import FileResponse, HTMLResponse

from app.models.user import User
from app.validators.user_validators import get_current_active_user
from app.utils.s3_connection import s3_client
from app.utils.extension_mapping import MEDIA_TYPES


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def get_index(current_user: Annotated[User, Depends(get_current_active_user)]):
    index_path = Path("frontend/index.html")
    return index_path.read_text(encoding="utf-8")


@router.post("/upload")
async def post_upload(
    current_user: Annotated[User, Depends(get_current_active_user)],
    file: UploadFile,
    path: Annotated[str, Form(...)],
):
    await s3_client.upload_file(file.file, path)


@router.post("/download")
async def post_download(
    current_user: Annotated[User, Depends(get_current_active_user)],
    path: Annotated[str, Form(...)],
    type: Annotated[str, Form(...)],
    back: BackgroundTasks,
):
    local_file_path, temp_folder_name = await s3_client.download_file(path, type)

    if not local_file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Something at this path was not found',
        )
    
    _, extension = os.path.splitext(local_file_path.split("/")[-1])

    back.add_task(s3_client.cleanup, f"storage/{temp_folder_name}")
    
    return FileResponse(local_file_path, media_type=MEDIA_TYPES.get(extension), background=back)


@router.post("/delete")
async def post_delete(
    path: Annotated[str, Form(...)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    await s3_client.delete_file(path)