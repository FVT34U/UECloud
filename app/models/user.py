from typing import Annotated, List
from fastapi import Cookie, Depends, HTTPException, status
import jwt
from pydantic import BaseModel, Field

from app.models.storage_entity import StorageEntityDescription
from app.models.token import TokenData, SECRET_KEY, ALGORITHM
from app.utils.mongodb_connection import get_collection_users
from app.utils.password_encription import verify_password


class User(BaseModel):
    _id: str
    username: str
    email: str | None = None
    telegram: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str
    available_storages: Annotated[List[StorageEntityDescription], Field(default_factory=list)]


def get_db_user(username: str):
    coll = get_collection_users()
    query = {"username": username}

    user = coll.find_one(query)

    if user:
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
    
    user = get_db_user(username=token_data.username)

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