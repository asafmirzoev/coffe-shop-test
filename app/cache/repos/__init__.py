from typing import TYPE_CHECKING

from app.cache.exceptions import CacheObjectDoesNotExist

if TYPE_CHECKING:
    from app.core.container import Container


class BaseCacheRepo:

    def __init__(self, container: type['Container']):
        self.container = container
        self.prefix_key = self.__class__.__name__.lower()

    @staticmethod
    async def check_object_exists(obj):
        if obj is None:
            raise CacheObjectDoesNotExist

    async def check_key_exists(self, key: str):
        exists = await self.container.redis_client.exists(key)
        if not exists:
            raise CacheObjectDoesNotExist
