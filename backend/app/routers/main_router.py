import os
from pathlib import Path
from typing import Annotated
import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Response, UploadFile,  status
from fastapi.responses import FileResponse, HTMLResponse

from app.models.user import User
from app.validators.user_validators import get_current_active_user
from app.utils.s3_connection import s3_client
from app.utils.extension_mapping import MEDIA_TYPES
from app.utils.mongodb_connection import get_collection_storage_entities
from app.models.storage_entity import StorageEntityInDB, StorageEntityUser
from app.models.storage_group import StorageEntityGroupList


router = APIRouter()


@router.post("/upload", response_class=Response)
async def post_upload(
    current_user: Annotated[User, Depends(get_current_active_user)],
    file: UploadFile,
    path: Annotated[str, Form(...)],
    parent_id: Annotated[str, Form(...)],
):
    response = await s3_client.upload_file(file.file, path)

    if not response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong during upload file",
        )
    
    coll = get_collection_storage_entities()

    se_in_db = StorageEntityInDB(
        _id=str(uuid.uuid4()),
        name=path.split("/")[-1],
        type='file',
        owner=current_user.username,
        parent=parent_id,
        path=path,
        groups=StorageEntityGroupList(),
        users=[StorageEntityUser(
            user=current_user,
            group=StorageEntityGroupList()[1],
        )]
    )

    result = coll.insert_one(
        se_in_db.model_dump(by_alias=True)
    )

    if not result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong during database insert operation",
        )
    
    return Response(status_code=200)


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

    #back.add_task(s3_client.cleanup, f"storage/{temp_folder_name}")
    
    return FileResponse(local_file_path, media_type=MEDIA_TYPES.get(extension))


@router.post("/create")
async def post_create(
    current_user: Annotated[User, Depends(get_current_active_user)],
    path: Annotated[str, Form(...)],
    type: Annotated[str, Form(...)],
    parent_id: Annotated[str, Form(...)],
):
    response = await s3_client.create_dir(path)

    if not response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong during upload file",
        )
    
    coll = get_collection_storage_entities()

    se_in_db = StorageEntityInDB(
        _id=str(uuid.uuid4()),
        name=path.split("/")[-1],
        type=type,
        owner=current_user.username,
        parent=parent_id,
        path=path,
        groups=StorageEntityGroupList(),
        users=[StorageEntityUser(
            user=current_user,
            group=StorageEntityGroupList()[1],
        )]
    )

    result = coll.insert_one(
        se_in_db.model_dump(by_alias=True)
    )

    if not result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong during database insert operation",
        )
    
    return Response(status_code=200)


@router.post("/delete")
async def post_delete(
    path: Annotated[str, Form(...)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    await s3_client.delete_file(path)