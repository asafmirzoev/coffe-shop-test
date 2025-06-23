from pydantic import BaseModel

from app.cache.models.user import UserCacheModel


class UsersCacheModel(BaseModel):
    users: list[UserCacheModel]
