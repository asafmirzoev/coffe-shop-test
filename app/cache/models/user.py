from typing import Optional
from pydantic import BaseModel


class UserCacheModel(BaseModel):
    id: int

    email: str
    first_name: Optional[str]
    last_name: Optional[str]

    verified: bool
    is_admin: bool
