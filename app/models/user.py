from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import BaseModel

from app.models.token import TokenData, SECRET_KEY, ALGORITHM
from app.utils.mongodb_connection import get_collection_users
from app.utils.password_encription import verify_password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    _id: str
    username: str
    email: str | None = None
    telegram: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


def get_user(username: str):
    coll = get_collection_users()
    query = {"username": username}

    user = coll.find_one(query)

    if user:
        return UserInDB(**user)
    

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username == "":
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)

    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Inactive user",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if current_user.disabled:
        raise credentials_exception
    return current_user