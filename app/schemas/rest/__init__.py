from typing import Any

from pydantic import BaseModel


class BasePaginatedResponse(BaseModel):
    next: bool
    previous: bool
    count: int
    data: list[Any]
