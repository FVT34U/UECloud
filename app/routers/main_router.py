from pathlib import Path
from typing import Annotated, List
import uuid
import aiofiles
from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse

from app.models.storage_entity import StorageEntity, StorageEntityDescription, StorageEntityList
from app.models.storage_group import StorageEntityGroupList
from app.models.user import User, get_current_active_user
from app.utils.mongodb_connection import get_collection_users, get_collection_workspaces
from app.utils.s3_connection import S3Client
from app.utils.extension_mapping import MEDIA_TYPES


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
    current_user: Annotated[User, Depends(get_current_active_user)],
    path: Annotated[str, Form(...)],
):
    await s3_client.upload_file(path)


@router.post("/download")
async def post_download(
    current_user: Annotated[User, Depends(get_current_active_user)],
    path: Annotated[str, Form(...)],
    back: BackgroundTasks,
):
    local_file_path = await s3_client.download_file(path)

    if not local_file_path:
        return
    
    extension = local_file_path.split("/")[-1].split(".")[-1]

    back.add_task(s3_client.cleanup, local_file_path)
    
    return FileResponse(local_file_path, media_type=MEDIA_TYPES.get(extension), background=back)


@router.post("/delete")
async def post_delete(
    path: Annotated[str, Form(...)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    await s3_client.delete_file(path)


@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/users/{username}/", response_model=User)
async def get_user_by_name(
    current_user: Annotated[User, Depends(get_current_active_user)],
    username: str,
):
    coll = get_collection_users()

    user = coll.find_one({"username": username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user does not exists",
        )
    
    return User(
        **user,
    )


@router.get("/workspaces/", response_model=StorageEntityList)
async def get_workspaces(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    coll = get_collection_workspaces()
    ws = coll.find({"owner":current_user.username})

    workspaces = StorageEntityList()

    for w in ws:
        workspaces.entity_list.append(StorageEntity(**w))

    return workspaces

@router.get("/workspaces/{workspace_name}", response_model=StorageEntity)
async def get_workspace_by_id(
    current_user: Annotated[User, Depends(get_current_active_user)],
    workspace_name: str,
):
    coll = get_collection_workspaces()

    ws = coll.find_one({"name":workspace_name})
    if not ws:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This workspace does not exests",
        )
    
    return StorageEntity(
        **ws,
    )

@router.post("/workspaces/create", response_class=JSONResponse)
async def post_create_workspace(
    current_user: Annotated[User, Depends(get_current_active_user)],
    workspace_name: Annotated[str, Form(...)]
):
    if workspace_name == "":
        return JSONResponse(
            {
                "status": "FAILED",
                "detail": "Empty workspace name",
            }
        )
    
    coll = get_collection_workspaces()
    test = coll.find_one({"name":workspace_name})
    if test:
        return JSONResponse(
            {
                "status": "FAILED",
                "detail": "Workspace name already used",
            }
        )

    id = str(uuid.uuid4())
    coll.insert_one(
        StorageEntity(
            _id=id,
            name=workspace_name,
            owner=current_user.username,
            groups=StorageEntityGroupList(),
        ).model_dump(by_alias=True)
    )

    ws = coll.find_one({"_id":id})
    if not ws:
        return JSONResponse(
            {
                "status": "FAILED",
                "detail": "Database error, workspace hasn't been added",
            }
        )
    
    user_coll = get_collection_users()
    
    user_coll.update_one(
        filter={
            "username": current_user.username,
        },
        update={
            '$push': {
                "available_storages": {
                    "entity_name": workspace_name,
                    "group_name": "owner",
                }
            }
        }
    )
    
    await s3_client.create_dir(workspace_name)

    return JSONResponse(
        {
            "status": "OK",
            "detail": "Successful create workspace",
        }
    )