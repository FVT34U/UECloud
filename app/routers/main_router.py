from pathlib import Path
from typing import Annotated, List
import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from app.models.storage_entity import StorageEntity, StorageEntityInDB, StorageEntityList, StorageEntityUser, get_available_workspaces, workspace_exists, workspace_name_is_free
from app.models.storage_group import StorageEntityGroup, StorageEntityGroupList
from app.models.user import User, get_current_active_user, get_db_user, user_exists, user_has_access_to_project, user_has_access_to_workspace
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
    user: Annotated[User, Depends(user_exists)],
):
    return user


@router.get("/workspaces/", response_model=StorageEntityList)
async def get_workspaces(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return await get_available_workspaces(current_user)


@router.post("/workspaces/create", response_model=StorageEntity)
async def post_create_workspace(
    back: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_active_user)],
    workspace_name: Annotated[str, Form(...)],
):
    if not await workspace_name_is_free(workspace_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workspace with this name is already exists",
        )

    coll = get_collection_workspaces()

    id = str(uuid.uuid4())
    group_list = StorageEntityGroupList()
    se_user = StorageEntityUser(
        user=current_user,
        group=group_list[1],
    )

    workspace_in_db = StorageEntityInDB(
        _id=id,
        name=workspace_name,
        type="workspace",
        owner=current_user.username,
        groups=StorageEntityGroupList(),
        inner_entities=list(),
        users=[se_user],
    )

    result = coll.insert_one(
        workspace_in_db.model_dump(by_alias=True)
    )

    if not result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong during database insert operation",
        )
    
    back.add_task(s3_client.create_dir, workspace_in_db.name)

    return await workspace_exists(workspace_in_db.name)


@router.get("/workspaces/{workspace_name}/", response_model=StorageEntity)
async def get_workspace_by_name(
    workspace: Annotated[StorageEntity, Depends(workspace_exists)],
    current_user: Annotated[
        User,
        Depends(get_current_active_user),
        Depends(user_has_access_to_workspace),
    ],
):
    return workspace


@router.get("/workspaces/{workspace_name}/projects", response_model=StorageEntityList)
async def get_projects_by_workspace(
    workspace: Annotated[StorageEntityInDB, Depends(workspace_exists)],
    current_user: Annotated[
        User,
        Depends(get_current_active_user),
        Depends(user_has_access_to_workspace),
    ],
):
    pass # TODO


@router.post("/workspaces/{workspace_name}/projects/create", response_class=JSONResponse)
async def post_create_project(
    workspace: Annotated[StorageEntity, Depends(workspace_exists)],
    current_user: Annotated[
        User,
        Depends(get_current_active_user),
        Depends(user_has_access_to_workspace),
    ],
    project_name: Annotated[str, Form(...)]
):
    pass # TODO


@router.get("/workspaces/{workspace_name}/projects/{project_name}", response_model=StorageEntity)
async def get_projects_by_workspace(
    current_user: Annotated[
        User,
        Depends(get_current_active_user),
        Depends(user_has_access_to_workspace),
        Depends(user_has_access_to_project),
    ],
    workspace_name: str,
    project_name: str,
):
    pass # TODO