from typing import Annotated, List
from pydantic import BaseModel, BeforeValidator, Field

from app.models.storage_group import StorageEntityGroup, StorageEntityGroupList
from app.models.user import User


class StorageEntity(BaseModel):
    id: str = Field(alias="_id")
    name: str
    type: str
    owner: str
    parent: str
    path: str


class StorageEntityUser(BaseModel):
    user: User
    group: StorageEntityGroup


class StorageEntityInDB(StorageEntity):
    groups: Annotated[List[StorageEntityGroup], BeforeValidator(StorageEntityGroupList.validate)]
    users: Annotated[List[StorageEntityUser], Field(default_factory=list)]


class StorageEntityList(BaseModel):
    parent_type: str = ''
    parent_path: str = ''
    entity_list: Annotated[List[StorageEntity], Field(default_factory=list)]
