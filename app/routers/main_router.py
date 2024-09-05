from pathlib import Path
from typing import Annotated
import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, status
import fastapi
from fastapi.responses import FileResponse, HTMLResponse

from app.models.storage_entity import *
from app.models.storage_group import StorageEntityGroupList
from app.models.user import User, get_current_active_user, user_exists, user_has_access_to_project, user_has_access_to_workspace
from app.utils.mongodb_connection import get_collection_storage_entities
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
    return await get_available_storage_entities(current_user, "workspace")


@router.post("/workspaces/create", response_model=StorageEntity)
async def post_create_workspace(
    back: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_active_user)],
    workspace_name: Annotated[str, Form(...)],
):
    if not await storage_entity_name_is_free(workspace_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workspace with this name is already exists",
        )

    coll = get_collection_storage_entities()

    id = str(uuid.uuid4())
    group_list = StorageEntityGroupList()
    se_user = StorageEntityUser(
        user=current_user,
        group=group_list[1],
    )

    se_in_db = StorageEntityInDB(
        _id=id,
        name=workspace_name,
        type="workspace",
        owner=current_user.username,
        parent="",
        groups=StorageEntityGroupList(),
        inner_entities=list(),
        users=[se_user],
    )

    result = coll.insert_one(
        se_in_db.model_dump(by_alias=True)
    )

    if not result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong during database insert operation",
        )
    
    back.add_task(s3_client.create_dir, se_in_db.name)

    return se_in_db


@router.get("/workspaces/{workspace_name}/", response_model=StorageEntity)
async def get_workspace_by_name(
    workspace_name: Annotated[str, fastapi.Path(...)],
    workspace: Annotated[StorageEntityInDB, Depends(lambda workspace_name: storage_entity_exists(se_name=workspace_name))],
    current_user: Annotated[
        User,
        Depends(get_current_active_user),
        Depends(user_has_access_to_workspace),
    ],
):
    return workspace


@router.get("/workspaces/{workspace_name}/projects", response_model=StorageEntityList)
async def get_projects_by_workspace(
    workspace_name: Annotated[str, fastapi.Path(...)],
    workspace: Annotated[StorageEntityInDB, Depends(lambda workspace_name: storage_entity_exists(se_name=workspace_name))],
    current_user: Annotated[
        User,
        Depends(get_current_active_user),
        Depends(user_has_access_to_workspace),
    ],
):
    return await get_available_storage_entities(current_user, "workspace", workspace.id)


@router.post("/workspaces/{workspace_name}/projects/create", response_model=StorageEntity)
async def post_create_project(
    back: BackgroundTasks,
    workspace_name: Annotated[str, fastapi.Path(...)],
    workspace: Annotated[StorageEntityInDB, Depends(lambda workspace_name: storage_entity_exists(se_name=workspace_name))],
    current_user: Annotated[
        User,
        Depends(get_current_active_user),
        Depends(user_has_access_to_workspace),
    ],
    project_name: Annotated[str, Form(...)],
):
    if not await storage_entity_name_is_free(project_name, workspace.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with this name is already exists",
        )

    coll = get_collection_storage_entities()

    id = str(uuid.uuid4())
    group_list = StorageEntityGroupList()
    se_user = StorageEntityUser(
        user=current_user,
        group=group_list[1],
    )

    se_in_db = StorageEntityInDB(
        _id=id,
        name=project_name,
        type="project",
        owner=current_user.username,
        parent=workspace.id,
        groups=StorageEntityGroupList(),
        inner_entities=list(),
        users=[se_user],
    )

    result = coll.insert_one(
        se_in_db.model_dump(by_alias=True)
    )

    if not result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong during database insert operation",
        )
    
    back.add_task(s3_client.create_dir, f"{workspace.name}/{project_name}")

    return se_in_db


@router.get("/workspaces/{workspace_name}/projects/{project_name}", response_model=StorageEntity)
async def get_projects_by_workspace(
    workspace_name: Annotated[str, fastapi.Path(...)],
    workspace: Annotated[StorageEntityInDB, Depends(lambda workspace_name: storage_entity_exists(se_name=workspace_name))],
    #project_name: Annotated[str, fastapi.Path(...)],
    #project: Annotated[StorageEntityInDB, Depends(lambda project_name: storage_entity_exists(project_name, workspace.id))],
    current_user: Annotated[
        User,
        Depends(get_current_active_user),
        Depends(user_has_access_to_workspace),
        Depends(user_has_access_to_project),
    ],
):
    pass # TODO