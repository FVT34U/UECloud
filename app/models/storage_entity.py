from typing import Annotated, List
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, BeforeValidator, Field

from app.models.storage_group import StorageEntityGroup, StorageEntityGroupList
from app.models.user import User, get_current_active_user, user_has_access_to_workspace
from app.utils.mongodb_connection import get_collection_workspaces


class StorageEntity(BaseModel):
    id: str = Field(alias="_id")
    name: str
    type: str
    owner: str


class StorageEntityUser(BaseModel):
    user: User
    group: StorageEntityGroup


class StorageEntityInDB(StorageEntity):
    groups: Annotated[List[StorageEntityGroup], BeforeValidator(StorageEntityGroupList.validate)]
    inner_entities: Annotated[List[StorageEntity], Field(default_factory=list)]
    users: Annotated[List[StorageEntityUser], Field(default_factory=list)]


class StorageEntityList(BaseModel):
    entity_list: Annotated[List[StorageEntity], Field(default_factory=list)]


async def get_available_workspaces(
    current_user: User,
) -> StorageEntityList:
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

    workspaces = StorageEntityList(entity_list=[StorageEntityInDB(**ws) for ws in wss])

    return workspaces


async def get_available_projects( # TODO: короче капец полный, надо чота думать по базе
    current_user: User,
    workspace: StorageEntityInDB,
) -> StorageEntityList:
    coll = get_collection_workspaces()
    projs = coll.find(
        {
            "name": workspace.name,
        },
        {
            "_id": 0,
            "inner_entities": 1,
        },
    )



async def workspace_exists(
    workspace_name: str,
) -> StorageEntityInDB:
    coll = get_collection_workspaces()
    ws = coll.find_one({"name": workspace_name})

    if not ws:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace doesn't exists"
        )
    
    return StorageEntityInDB(**ws)


async def workspace_name_is_free(
    workspace_name: str,
) -> bool:
    coll = get_collection_workspaces()
    ws = coll.find_one({"name": workspace_name})

    if ws:
        return False
    
    return True
