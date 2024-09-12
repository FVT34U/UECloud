from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Optional
import uuid
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, Form, HTTPException, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user import User
from app.validators.user_validators import authenticate_user, get_current_active_user, get_db_user
from app.utils.mongodb_connection import get_collection_users
from app.models.token import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from app.utils.password_encription import get_password_hash


router = APIRouter()


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    response = Response(status_code=200)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite='none',
        max_age=604800,
    )

    return response


@router.get("/login", response_class=HTMLResponse)
async def get_login():
    index_path = Path("frontend/login.html")
    return index_path.read_text(encoding="utf-8")


@router.get("/register", response_class=HTMLResponse)
async def get_register():
    index_path = Path("frontend/register.html")
    return index_path.read_text(encoding="utf-8")


@router.post("/register", response_class=RedirectResponse)
async def post_register(
    username: Annotated[str, Form(...)],
    password: Annotated[str, Form(...)],
    email: Annotated[Optional[str], Form(...)] = None,
    telegram: Annotated[Optional[str], Form(...)] = None,
):
    user = get_db_user(username)
    
    if user:
        return RedirectResponse("/register", status_code=302)

    coll = get_collection_users()
    coll.insert_one(
        {
            "_id": str(uuid.uuid4()),
            "username": username,
            "hashed_password": get_password_hash(password),
            "email": email,
            "telegram": telegram,
            "disabled": False,
        }
    )

    return RedirectResponse("/login", status_code=302)


@router.get("/logout")
async def get_logout(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    response = Response(status_code=200)
    response.delete_cookie(key="access_token")

    return response