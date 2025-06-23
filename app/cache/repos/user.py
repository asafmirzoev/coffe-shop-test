import datetime

from app.db.models.user import UserDbModel

from app.cache.repos import BaseCacheRepo
from app.cache.models.user import UserCacheModel


class UserCacheRepo(BaseCacheRepo):

    async def get(self, _id: int) -> UserCacheModel:
        key = await self._get_key(_id)
        value = await self.container.redis_client.get(key)
        await self.check_object_exists(value)

        user_cache_model = UserCacheModel.model_validate_json(value)

        await self.container.redis_client.expire(
            key,
            datetime.timedelta(hours=1),
        )
        return user_cache_model

    async def set(self, user_db_model: UserDbModel):
        key = await self._get_key(user_db_model.id)
        user_cache_model = await self.db_model_to_cache(user_db_model)
        await self.container.redis_client.set(
            key,
            user_cache_model.model_dump_json(),
            ex=datetime.timedelta(hours=1),
        )
        return user_cache_model

    async def update(self, user_cache_model: UserCacheModel):
        key = await self._get_key(user_cache_model.id)
        await self.container.redis_client.set(
            key,
            user_cache_model.model_dump_json(),
            ex=datetime.timedelta(hours=1),
        )

    async def delete(self, _id: int):
        key = await self._get_key(_id)
        await self.container.redis_client.delete(key)

    async def set_verification_code(
        self,
        _id: int,
        code: int,
    ):
        key = await self._get_key(_id)
        await self.container.redis_client.set(
            f'{key}-verification-code',
            str(code),
            ex=datetime.timedelta(days=2),
        )
        await self.container.redis_client.set(
            f'{key}-verification-code-limit',
            str(code),
            ex=datetime.timedelta(minutes=1),
        )

    async def check_verification_code(self, _id: int, code: int) -> bool:
        key = await self._get_key(_id)
        saved_code = await self.container.redis_client.get(f'{key}-verification-code')

        if not saved_code:
            return False

        return saved_code == str(code)

    async def check_verification_code_limit(self, _id: int) -> bool:
        key = await self._get_key(_id)
        limit_exists = await self.container.redis_client.get(
            f'{key}-verification-code-limit'
        )
        return bool(limit_exists)

    async def db_model_to_cache(
        self,
        user_db_model: UserDbModel,
    ):
        return UserCacheModel(
            id=user_db_model.id,
            email=user_db_model.email,
            first_name=user_db_model.first_name,
            last_name=user_db_model.last_name,
            verified=user_db_model.verified,
            is_admin=user_db_model.is_admin,
        )

    async def _get_key(
        self,
        _id: int,
    ):
        return f'{self.prefix_key}:{_id}'
