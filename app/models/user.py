from typing import Annotated
from fastapi import Cookie, Depends, HTTPException, status
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


# Realization with PasswordBearer:
#
# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
    
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         print(f"[LOG]: ON GET CURRENT USER: username is {username}")
#         if username == "":
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except jwt.InvalidTokenError:
#         print("[LOG]: ON GET CURRENT USER: got jwt.InvalidTokenError")
#         raise credentials_exception
    
#     user = get_user(username=token_data.username)

#     if user is None:
#         print("[LOG]: ON GET CURRENT USER: user is None")
#         raise credentials_exception
#     return user


async def get_current_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is None",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print(f"[LOG]: ON GET CURRENT USER: username is {username}")
        if username == "":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Empty username",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(username=username)
    except jwt.InvalidTokenError:
        print("[LOG]: ON GET CURRENT USER: got jwt.InvalidTokenError")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="jwt.InvalidTokenError",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_db_user(username=token_data.username)

    if user is None:
        print("[LOG]: ON GET CURRENT USER: user is None")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is None",
            headers={"WWW-Authenticate": "Bearer"},
        )
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