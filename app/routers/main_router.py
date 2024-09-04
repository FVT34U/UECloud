from pathlib import Path
from typing import Annotated, List
import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from app.models.storage_entity import StorageEntity, StorageEntityInDB, StorageEntityList, StorageEntityUser
from app.models.storage_group import StorageEntityGroup, StorageEntityGroupList
from app.models.user import User, get_current_active_user, get_db_user, user_has_access_to_project, user_has_access_to_workspace
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
    user = get_db_user(username)
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
    ws_coll = get_collection_workspaces()
    wss = ws_coll.find(
        {
            "users": {
                "$elemMatch": {
                    "user": current_user.username,
                },
            },
        }
    )

    workspaces = StorageEntityList(entity_list=[StorageEntity(**ws) for ws in wss])

    return workspaces


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
    test = coll.find_one({"name": workspace_name})
    if test:
        return JSONResponse(
            {
                "status": "FAILED",
                "detail": "Workspace name already used",
            }
        )

    id = str(uuid.uuid4())
    group_list = StorageEntityGroupList()
    se_user = StorageEntityUser(
        user=current_user,
        group=group_list[1],
    )
    workspace = StorageEntityInDB(
        _id = id,
        name = workspace_name,
        type="workspace",
        owner = current_user.username,
        groups = StorageEntityGroupList(),
        inner_entities=list(),
        users=[se_user],
    )

    coll.insert_one(
        workspace.model_dump(by_alias=True)
    )

    ws = coll.find_one({"_id": id})
    if not ws:
        return JSONResponse(
            {
                "status": "FAILED",
                "detail": "Database error, workspace hasn't been added",
            }
        )
    
    await s3_client.create_dir(workspace_name)

    return JSONResponse(
        {
            "status": "OK",
            "detail": "Successful create workspace",
        }
    )


@router.get("/workspaces/{workspace_name}/", response_model=StorageEntity)
async def get_workspace_by_name(
    current_user: Annotated[User, Depends(get_current_active_user), Depends(user_has_access_to_workspace)],
    workspace_name: str,
):
    w_coll = get_collection_workspaces()

    ws = w_coll.find_one({"name": workspace_name})
    if not ws:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This workspace does not exests",
        )
    
    return StorageEntity(
        **ws,
    )


@router.get("/workspaces/{workspace_name}/projects", response_model=StorageEntityList)
async def get_projects_by_workspace(
    current_user: Annotated[User, Depends(get_current_active_user), Depends(user_has_access_to_workspace)],
    workspace_name: str,
):
    pass



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
    pass


@router.post("/workspaces/{workspace_name}/projects/create", response_class=JSONResponse)
async def post_create_project(
    current_user: Annotated[
        User,
        Depends(get_current_active_user),
        Depends(user_has_access_to_workspace),
    ],
    project_name: Annotated[str, Form(...)]
):
    pass