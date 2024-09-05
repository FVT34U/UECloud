from typing import Annotated, List
from fastapi import HTTPException, status
from pydantic import BaseModel, BeforeValidator, Field

from app.models.storage_group import StorageEntityGroup, StorageEntityGroupList
from app.models.user import User
from app.utils.mongodb_connection import get_collection_storage_entities


class StorageEntity(BaseModel):
    id: str = Field(alias="_id")
    name: str
    type: str
    owner: str
    parent: str


class StorageEntityUser(BaseModel):
    user: User
    group: StorageEntityGroup


class StorageEntityInDB(StorageEntity):
    groups: Annotated[List[StorageEntityGroup], BeforeValidator(StorageEntityGroupList.validate)]
    users: Annotated[List[StorageEntityUser], Field(default_factory=list)]


class StorageEntityList(BaseModel):
    entity_list: Annotated[List[StorageEntity], Field(default_factory=list)]


async def get_available_storage_entities(
    current_user: User,
    type: str,
    parent_id: str = "",
) -> StorageEntityList:
    coll = get_collection_storage_entities()

    query = {
        "type": type,
        "parent": parent_id,
        "users": {
            "$elemMatch": {
                "user.username": current_user.username,
            }
        }
    }

    ses = coll.find(query)
    storage_entities = StorageEntityList(entity_list=[StorageEntityInDB(**se) for se in ses])

    return storage_entities


def storage_entity_exists(
    se_name: str,
    parent_id: str = "",
) -> StorageEntityInDB:
    coll = get_collection_storage_entities()
    st = coll.find_one(
        {
            "name": se_name,
            "parent": parent_id,
        }
    )

    if not st:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storage Entity doesn't exists"
        )
    
    return StorageEntityInDB(**st)


async def storage_entity_name_is_free(
    se_name: str,
    parent_id: str = "",
) -> bool:
    coll = get_collection_storage_entities()
    st = coll.find_one(
        {
            "name": se_name,
            "parent": parent_id,
        }
    )

    if st:
        return False
    
    return True
