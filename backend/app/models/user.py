from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str | None = None
    telegram: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    _id: str
    hashed_password: str