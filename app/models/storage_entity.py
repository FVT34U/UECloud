from typing import Annotated, List
from pydantic import BaseModel, BeforeValidator

from app.models.storage_group import StorageEntityGroup, StorageEntityGroupList


class StorageEntity(BaseModel):
    _id: str
    path: str
    owner: str
    groups: Annotated[List[StorageEntityGroup], BeforeValidator(StorageEntityGroupList.validate)]


if __name__ == "__main__":
    l = StorageEntity(
        _id="1234",
        path="home/test/12",
        owner="admin",
        groups=StorageEntityGroupList(),
    )

    print(l)
