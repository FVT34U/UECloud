from typing import Annotated
from fastapi import Cookie, Depends, HTTPException, status
import jwt
from pydantic import BaseModel

from app.models.token import TokenData, SECRET_KEY, ALGORITHM
from app.utils.mongodb_connection import get_collection_users, get_collection_workspaces
from app.utils.password_encription import verify_password


class User(BaseModel):
    username: str
    email: str | None = None
    telegram: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    _id: str
    hashed_password: str


def get_db_user(username: str):
    coll = get_collection_users()
    query = {"username": username}

    user = coll.find_one(query)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exists"
        )
    
    return UserInDB(**user)
    

def authenticate_user(username: str, password: str):
    user = get_db_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is None",
        )
    
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username == "":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Empty username",
            )
        token_data = TokenData(username=username)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="jwt.InvalidTokenError",
        )
    
    user = User(**get_db_user(username=token_data.username).model_dump())

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is None",
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Inactive user",
    )

    if current_user.disabled:
        raise credentials_exception
    return current_user


async def user_exists(
    username: str,
) -> User:
    coll = get_collection_users()
    user = coll.find_one({"username": username})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exists"
        )
    
    return User(**user)


async def user_has_access_to_workspace(
    workspace_name: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    ws_coll = get_collection_workspaces()

    from app.models.storage_entity import StorageEntityInDB
    ws_in_db = StorageEntityInDB(**ws_coll.find_one({"name": workspace_name}))

    users = [ws_user.user for ws_user in ws_in_db.users]

    if current_user not in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't have permission to see this workspace",
        )
    
    return current_user


async def user_has_access_to_project(
    workspace_name: str,
    project_name: str,
    current_user: Annotated[User, Depends(get_current_active_user), Depends(user_has_access_to_workspace)],
):
    return current_user