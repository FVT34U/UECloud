from typing import Annotated
from fastapi import APIRouter, Depends

from app.models.user import User
from app.validators.user_validators import get_current_active_user, user_exists


router = APIRouter(
    prefix="/users"
)


@router.get("/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/{username}/", response_model=User)
async def get_user_by_name(
    current_user: Annotated[User, Depends(get_current_active_user)],
    user: Annotated[User, Depends(user_exists)],
):
    return user