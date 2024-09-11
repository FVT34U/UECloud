from fastapi import HTTPException, status

from app.models.storage_entity import StorageEntityInDB, StorageEntityList
from app.models.user import User
from app.utils.mongodb_connection import get_collection_storage_entities


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

    test = coll.count_documents(query)

    if test == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Can't find anything for some reason",
        )
    
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