from typing import Optional

from pydantic import BaseModel

from app.cache.models.user import UserCacheModel
from app.schemas.rest import BasePaginatedResponse


class MeResponse(BaseModel):
    user: UserCacheModel


class UsersResponse(BasePaginatedResponse):
    data: list[UserCacheModel]


class UpdateUserRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
