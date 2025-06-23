from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Query, Path, status

from app.api.rest import get_current_verified_user, get_current_admin_user
from app.cache.models.user import UserCacheModel
from app.core.container import Container

from app.api import get_db_session
from app.schemas.rest.users import MeResponse, UpdateUserRequest, UsersResponse

router = APIRouter(
    prefix='/users',
    tags=['users'],
)


@router.get(
    '/me',
    response_model=MeResponse,
    summary='Me',
    description='Endpoint to get information about the current user',
)
async def me(
    curren_user: UserCacheModel = Depends(get_current_verified_user),
):
    return await Container.users_service.me(curren_user)


@router.get(
    '/users/{user_id}',
    response_model=MeResponse,
    summary='User info by id',
    description='Endpoint to get information about the user by id',
)
async def user(
    user_id: Annotated[int, Path(ge=1)],
    curren_user: UserCacheModel = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    return await Container.users_service.user(
        user_id,
        session,
    )


@router.patch(
    '/users/{user_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Update user info by id',
    description='Endpoint to update user information by id',
)
async def update_user(
    user_id: Annotated[int, Path(ge=1)],
    request_schema: UpdateUserRequest,
    curren_user: UserCacheModel = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    return await Container.users_service.update_user(
        user_id,
        request_schema,
        session,
    )


@router.delete(
    '/users/{user_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete user by id',
    description='Endpoint to delete user by id',
)
async def delete_user(
    user_id: Annotated[int, Path(ge=1)],
    curren_user: UserCacheModel = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    return await Container.users_service.delete_user(
        user_id,
        session,
    )


@router.get(
    '/users',
    response_model=UsersResponse,
    summary='Users list',
    description='Endpoint to get information about the current user',
)
async def users(
    page: Annotated[int, Query(ge=1)] = 1,
    curren_user: UserCacheModel = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    return await Container.users_service.users(
        page,
        session,
    )
