from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.models.user import UserCacheModel
from app.core.environment import env
from app.core.exceptions import raise_exception, NotFoundException, ErrorMessageCodes
from app.db.exceptions import DbObjectDoesNotExist
from app.schemas.rest.users import UsersResponse, MeResponse, UpdateUserRequest
from app.services import BaseService


class UsersService(BaseService):

    async def me(self, current_user: UserCacheModel) -> MeResponse:
        return MeResponse(user=current_user)

    async def user(self, user_id: int, session: AsyncSession) -> MeResponse:
        try:
            user_cache_model = await self.container.user_union.get(
                user_id,
                session=session,
            )
        except DbObjectDoesNotExist:
            raise raise_exception(
                NotFoundException,
                ErrorMessageCodes.USER_NOT_FOUND,
            )

        return MeResponse(user=user_cache_model)

    async def update_user(
        self,
        user_id: int,
        request_schema: UpdateUserRequest,
        session: AsyncSession,
    ):
        try:
            user_cache_model = await self.container.user_union.get(
                user_id,
                session=session,
            )
        except DbObjectDoesNotExist:
            raise raise_exception(
                NotFoundException,
                ErrorMessageCodes.USER_NOT_FOUND,
            )

        if not (request_schema.first_name or request_schema.last_name):
            return

        update_values = dict()
        if request_schema.first_name:
            user_cache_model.first_name = request_schema.first_name
            update_values['first_name'] = request_schema.first_name

        if request_schema.last_name:
            user_cache_model.last_name = request_schema.last_name
            update_values['last_name'] = request_schema.last_name

        await self.container.user_union.update(
            user_cache_model,
            values=update_values,
            session=session,
        )

    async def delete_user(self, user_id: int, session: AsyncSession):
        try:
            user_cache_model = await self.container.user_union.get(
                user_id,
                session=session,
            )
        except DbObjectDoesNotExist:
            raise raise_exception(
                NotFoundException,
                ErrorMessageCodes.USER_NOT_FOUND,
            )

        await self.container.user_union.delete(
            user_cache_model.id,
            session=session,
        )

    async def users(self, page: int, session: AsyncSession) -> UsersResponse:
        end_index = page * env.pagination_items
        start_index = end_index - env.pagination_items

        users_count = await self.container.user_db_repo.count(
            session=session,
        )
        user_cache_models = await self.container.user_union.all(
            page,
            start_index,
            env.pagination_items,
            session=session,
        )
        return UsersResponse(
            next=users_count > end_index,
            previous=min(end_index, users_count) >= env.pagination_items,
            count=users_count,
            data=user_cache_models,
        )
