from datetime import datetime, date
from typing import Optional
from pydantic import EmailStr

from pydantic import BaseModel


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class JwtTokenPayload(BaseModel):
    id: int
    type: str
    exp: datetime


class JWTResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expires: datetime


class SignInRequest(BaseModel):
    email: EmailStr
    password: str
