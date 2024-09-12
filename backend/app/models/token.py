from datetime import datetime, timedelta, timezone
import jwt
from pydantic import BaseModel


SECRET_KEY = "9d20a9b4fd024e40fabe0765bfeb78fdfa33e71d991a82ff9b616ff40280af4a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt