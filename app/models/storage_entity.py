from typing import Annotated, List
from pydantic import BaseModel, BeforeValidator, Field

from app.models.storage_group import StorageEntityGroup, StorageEntityGroupList


class StorageEntity(BaseModel):
    id: str = Field(alias="_id")
    name: str
    owner: str
    groups: Annotated[List[StorageEntityGroup], BeforeValidator(StorageEntityGroupList.validate)]


class StorageEntityList(BaseModel):
    entity_list: Annotated[List[StorageEntity], Field(default_factory=list)]


class StorageEntityDescription(BaseModel):
    entity_name: str
    group_name: str = "observer"
