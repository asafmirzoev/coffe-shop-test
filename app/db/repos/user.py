from typing import Any

from sqlalchemy import select, update, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import UserDbModel
from app.db.repos import BaseDbRepo


class UserDbRepo(BaseDbRepo):

    async def get(
        self,
        _id: int,
        session: AsyncSession,
    ):
        result = await session.execute(select(UserDbModel).where(UserDbModel.id == _id))
        user_db_model = result.scalar_one_or_none()
        await self.check_object_exists(user_db_model)
        return user_db_model

    async def get_by_email(
        self,
        email: str,
        session: AsyncSession,
    ):
        result = await session.execute(
            select(UserDbModel).where(UserDbModel.email == email)
        )
        user_db_model = result.scalar_one_or_none()
        await self.check_object_exists(user_db_model)
        return user_db_model

    async def all(
        self,
        offset: int,
        limit: int,
        session: AsyncSession,
    ):
        result = await session.execute(select(UserDbModel).offset(offset).limit(limit))
        return result.scalars().all()

    async def create(
        self,
        user_db_model: UserDbModel,
        session: AsyncSession,
    ):
        session.add(user_db_model)
        await session.commit()
        await session.refresh(user_db_model)

    async def update(
        self,
        _id: int,
        values: dict[str, Any],
        session: AsyncSession,
    ):
        await session.execute(
            update(UserDbModel).where(UserDbModel.id == _id).values(values)
        )
        await session.commit()

    async def delete(
        self,
        _id: int,
        session: AsyncSession,
    ):
        await session.execute(delete(UserDbModel).where(UserDbModel.id == _id))
        await session.commit()

    async def exists(
        self,
        email: str,
        session: AsyncSession,
    ) -> bool:
        result = await session.execute(
            select(func.count(UserDbModel.id)).where(
                UserDbModel.email == email,
            )
        )
        return bool(result.scalar())

    async def count(
        self,
        session: AsyncSession,
    ) -> int:
        result = await session.execute(select(func.count(UserDbModel.id)))
        return result.scalar()

    async def get_password_hash(self, _id: int, session: AsyncSession):
        result = await session.execute(
            select(UserDbModel.password).where(UserDbModel.id == _id)
        )
        password_hash = result.scalar_one_or_none()
        await self.check_object_exists(password_hash)
        return password_hash
