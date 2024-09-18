from copy import deepcopy
from typing import Annotated
import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, status
import fastapi

from app.models.storage_entity import StorageEntity, StorageEntityInDB, StorageEntityList, StorageEntityUser
from app.models.storage_group import StorageEntityGroupList
from app.models.user import User
from app.utils.mongodb_connection import get_collection_storage_entities
from app.validators.storage_entity_validators import get_available_storage_entities, storage_entity_exists, storage_entity_name_is_free
from app.validators.user_validators import get_current_active_user, user_has_access_to_project, user_has_access_to_workspace
from app.utils.s3_connection import s3_client


router = APIRouter(
    prefix="/workspace",
)


"""
New realization
Just want to resolving path and checking permissions for any action
Wish me some luck and patient
"""


async def resolve_path(
    current_user: Annotated[User, Depends(get_current_active_user)],
    path: str,
) -> StorageEntityList:
    if path == "/":
        return await get_available_storage_entities(current_user, "")
    
    print(f"path: {path}")
    
    entities = path.split("/")
    
    try:
        while True:
            entities.remove("")
    except ValueError:
        pass
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Can't parse current path",
        )
    
    coll = get_collection_storage_entities()

    if len(entities) == 1:
        ent = coll.find_one(
            {
                "type": "workspace",
                "name": entities[0],
                "parent": "",
                "users": {
                    "$elemMatch": {
                        "user.username": current_user.username,
                    }
                }
            }
        )

        if not ent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This entity doesn't exists or you doesn't have permission to see this entity",
            )
        
        return await get_available_storage_entities(current_user, ent.get("_id"))

    current_name = entities[-1]

    current_doc = coll.find_one({"name": current_name})
    endpoint = deepcopy(current_doc)
    
    if not current_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Endpoint doesn't exists",
        )

    for parent_name in reversed(entities[:-1]):
        parent_id = current_doc.get("parent")
        if not parent_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This entity doesn't exists",
            )

        current_doc = coll.find_one({"_id": parent_id})

        if not current_doc or current_doc.get("name") != parent_name:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This entity doesn't exists",
            )
        
    #print(endpoint)

    return await get_available_storage_entities(current_user, endpoint.get("_id"))
    

@router.get("/{path:path}", response_model=StorageEntityList)
async def get_content_by_path(
    current_user: Annotated[User, Depends(get_current_active_user)],
    storage_entities: Annotated[StorageEntityList, Depends(resolve_path)],
):
    return storage_entities


@router.post("/{path:path}/create", response_model=StorageEntity)
async def post_create_entity(
    path: str, # TODO: сделать зависимость для проверки пути)))
    back: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_active_user)],
    entity_name: Annotated[str, Form(...)], # TODO: проверить имя что не занято и не пустое
    entity_type: Annotated[str, Form(...)], # TODO: сделать зависмость на проверку типа + тип подсасывать из какого-нибудь списка
):
    coll = get_collection_storage_entities()

    id = str(uuid.uuid4())
    group_list = StorageEntityGroupList()
    se_user = StorageEntityUser(
        user=current_user,
        group=group_list[1],
    )

    splitted_path = path.split("/")
    parent_name = splitted_path[-1] # TODO: исправить потом, т.к. пути могут быть некорректные
    
    try:
        while True:
            splitted_path.remove("")
    except:
        pass

    correct_path = "/".join(splitted_path)

    parent = {"_id":"", "type":"", "path":""}
    if entity_type != "workspace":
        parent = coll.find_one({"name": parent_name})

    path_to_new_entity = f"{correct_path}/{entity_name}" # TODO: возможно поменять после написания проверки

    se_in_db = StorageEntityInDB(
        _id=id,
        name=entity_name,
        type=entity_type,
        owner=current_user.username,
        parent=parent.get("_id"),
        path=path_to_new_entity,
        groups=StorageEntityGroupList(),
        users=[se_user], # TODO: от типа энтити должен зависеть список пользователей, автоматом добавить всех из родителя, если это папка
    )

    result = coll.insert_one(
        se_in_db.model_dump(by_alias=True)
    )

    if not result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong during database insert operation",
        )
    
    back.add_task(s3_client.create_dir, path_to_new_entity)

    return se_in_db


"""
Strange part
I want to delete it, but need information from this code
"""

old_router = APIRouter()

@old_router.get("/workspaces/", response_model=StorageEntityList)
async def get_workspaces(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return await get_available_storage_entities(current_user, "workspace")


@old_router.post("/workspaces/create", response_model=StorageEntity)
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


@old_router.get("/workspaces/{workspace_name}/", response_model=StorageEntity)
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


@old_router.get("/workspaces/{workspace_name}/projects", response_model=StorageEntityList)
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


@old_router.post("/workspaces/{workspace_name}/projects/create", response_model=StorageEntity)
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


@old_router.get("/workspaces/{workspace_name}/projects/{project_name}", response_model=StorageEntity)
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