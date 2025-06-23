import datetime

from app.cache.models.users import UsersCacheModel
from app.db.models.user import UserDbModel

from app.cache.repos import BaseCacheRepo
from app.cache.models.user import UserCacheModel


class UsersCacheRepo(BaseCacheRepo):

    async def get(self, page: int) -> list[UserCacheModel]:
        value = await self.container.redis_client.hget(self.prefix_key, str(page))
        await self.check_object_exists(value)

        users_cache_model = UsersCacheModel.model_validate_json(value)

        await self.container.redis_client.expire(
            self.prefix_key,
            datetime.timedelta(hours=1),
        )
        return users_cache_model.users

    async def set(
        self, page: int, user_db_models: list[UserDbModel]
    ) -> list[UserCacheModel]:

        user_cache_models = list()

        for user_db_model in user_db_models:
            user_cache_model = await self.container.user_cache_repo.db_model_to_cache(
                user_db_model
            )
            user_cache_models.append(user_cache_model)

        users_cache_model = UsersCacheModel(
            users=user_cache_models,
        )
        await self.container.redis_client.hset(
            self.prefix_key, str(page), users_cache_model.model_dump_json()
        )
        await self.container.redis_client.expire(
            self.prefix_key,
            datetime.timedelta(hours=1),
        )
        return user_cache_models

    async def clear(self):
        await self.container.redis_client.delete(self.prefix_key)
