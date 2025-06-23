from typing import Any

import argon2.exceptions
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.exceptions import DbObjectDoesNotExist
from app.db.models.user import UserDbModel

from app.cache.exceptions import CacheObjectDoesNotExist
from app.cache.models.user import UserCacheModel

from app.unions import BaseUnion


class UserUnion(BaseUnion):

    async def get(
        self,
        _id: int,
        session: AsyncSession,
    ) -> UserCacheModel:
        try:
            user_cache_model = await self.container.user_cache_repo.get(
                _id,
            )
        except CacheObjectDoesNotExist:
            user_db_model = await self.container.user_db_repo.get(
                _id,
                session=session,
            )

            user_cache_model = await self.container.user_cache_repo.set(
                user_db_model,
            )

        return user_cache_model

    async def get_by_email(
        self,
        email: str,
        session: AsyncSession,
    ) -> UserCacheModel:
        user_db_model = await self.container.user_db_repo.get_by_email(
            email,
            session=session,
        )

        user_cache_model = await self.container.user_cache_repo.set(
            user_db_model,
        )

        return user_cache_model

    async def all(
        self,
        page: int,
        offset: int,
        limit: int,
        session: AsyncSession,
    ) -> list[UserCacheModel]:
        try:
            user_cache_models = await self.container.users_cache_repo.get(page)
        except CacheObjectDoesNotExist:
            user_cache_models = list()

        if not user_cache_models:
            user_db_models = await self.container.user_db_repo.all(
                offset,
                limit,
                session=session,
            )
            user_cache_models = await self.container.users_cache_repo.set(
                page,
                user_db_models,
            )
        return user_cache_models

    async def create(
        self,
        user_db_model: UserDbModel,
        session: AsyncSession,
    ) -> UserCacheModel:
        await self.container.user_db_repo.create(
            user_db_model,
            session=session,
        )
        await self.container.users_cache_repo.clear()
        user_cache_model = await self.get(
            user_db_model.id,
            session=session,
        )
        return user_cache_model

    async def update(
        self,
        user_cache_model: UserCacheModel,
        values: dict[str, Any],
        session: AsyncSession,
    ) -> UserCacheModel:
        await self.container.user_db_repo.update(
            user_cache_model.id,
            values,
            session=session,
        )
        await self.container.user_cache_repo.update(user_cache_model)
        await self.container.users_cache_repo.clear()
        return user_cache_model

    async def delete(self, _id: int, session: AsyncSession):
        await self.container.user_db_repo.delete(_id, session=session)
        await self.container.user_cache_repo.delete(_id)
        await self.container.users_cache_repo.clear()

    async def verify_password(
        self,
        _id: int,
        password: str,
        session: AsyncSession,
    ) -> bool:
        try:
            password_hash = await self.container.user_db_repo.get_password_hash(
                _id,
                session=session,
            )
        except DbObjectDoesNotExist:
            return False

        try:
            password_verified = self.container.password_hasher.verify(
                password_hash,
                password,
            )
        except (
            argon2.exceptions.VerifyMismatchError,
            argon2.exceptions.VerificationError,
            argon2.exceptions.InvalidHashError,
        ):
            return False

        return password_verified
