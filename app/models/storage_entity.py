from typing import Annotated, List
from pydantic import BaseModel, BeforeValidator, Field

from app.models.storage_group import StorageEntityGroup, StorageEntityGroupList
from app.models.user import User
from app.utils.mongodb_connection import get_collection_workspaces


class StorageEntity(BaseModel):
    id: str = Field(alias="_id")
    name: str
    owner: str
    groups: Annotated[List[StorageEntityGroup], BeforeValidator(StorageEntityGroupList.validate)]


class StorageEntityList(BaseModel):
    entity_list: Annotated[List[StorageEntity], Field(default_factory=list)]


if __name__ == "__main__":
    l = StorageEntity(
        _id="1234",
        path="home/test/12",
        owner="admin",
        groups=StorageEntityGroupList(),
    )

    print(l)
