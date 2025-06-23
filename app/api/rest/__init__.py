"""
I created the ‘rest’ directory so that when adding other approaches, such as graphql, just add the ‘graphql’ directory
"""

from typing import Optional

import jwt
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import get_db_session
from app.cache.models.user import UserCacheModel
from app.db.exceptions import DbObjectDoesNotExist

from app.core.authentication import JWTBearer
from app.core.environment import env
from app.core.exceptions import UnauthorizedException


async def get_current_user(
    token: str = Depends(JWTBearer()),
    session: AsyncSession = Depends(get_db_session),
) -> UserCacheModel:
    from app.core.container import Container

    try:
        payload = jwt.decode(
            token,
            env.jwt_secretkey.get_secret_value(),
            algorithms=[env.jwt_algorithm],
        )
    except Exception:
        raise UnauthorizedException(detail='Could not validate credentials')

    token_type = payload.get('type', None)
    if token_type != 'access':
        raise UnauthorizedException(detail='Could not validate credentials')
    user_id = int(payload['id'])

    try:
        user_cache_model = await Container.user_union.get(
            user_id,
            session=session,
        )
    except DbObjectDoesNotExist:
        raise UnauthorizedException(detail='Could not validate credentials')

    return user_cache_model


async def get_current_unverified_user(
    token: str = Depends(JWTBearer()),
    session: AsyncSession = Depends(get_db_session),
) -> UserCacheModel:
    user_cache_model = await get_current_user(
        token,
        session=session,
    )

    if user_cache_model.verified:
        raise UnauthorizedException(detail='User already verified')

    return user_cache_model


async def get_current_verified_user(
    token: str = Depends(JWTBearer()),
    session: AsyncSession = Depends(get_db_session),
) -> UserCacheModel:
    user_cache_model = await get_current_user(
        token,
        session=session,
    )

    if not user_cache_model.verified:
        raise UnauthorizedException(detail='User is not verified')

    return user_cache_model


async def get_current_admin_user(
    token: str = Depends(JWTBearer()),
    session: AsyncSession = Depends(get_db_session),
) -> UserCacheModel:
    user_cache_model = await get_current_verified_user(
        token,
        session=session,
    )

    if not user_cache_model.is_admin:
        raise UnauthorizedException(detail='You\'re not an admin.')

    return user_cache_model
