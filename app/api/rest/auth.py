from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status, Body

from app.api.rest import get_current_unverified_user
from app.cache.models.user import UserCacheModel
from app.core.container import Container

from app.api import get_db_session
from app.schemas.rest.auth import SignUpRequest, JWTResponse, SignInRequest


router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


@router.post(
    '/sign-up',
    response_model=JWTResponse,
    summary='Sign Up',
    description='Endpoint for user registration by email',
)
async def sign_up(
    request_schema: SignUpRequest,
    session: AsyncSession = Depends(get_db_session),
):
    return await Container.auth_service.sign_up(
        request_schema,
        session,
    )


@router.post(
    '/resend-verification-code',
    summary='Resend Verification Code',
    description='Endpoint for resend verification code',
    status_code=status.HTTP_200_OK,
)
async def resend_verification_code(
    current_user: UserCacheModel = Depends(get_current_unverified_user),
):
    return await Container.auth_service.resend_verification_code(
        current_user,
    )


@router.post(
    '/check-verification-code',
    response_model=JWTResponse,
    summary='Check Verification Code',
    description='Endpoint for check verification code',
)
async def check_verification_code(
    code: Annotated[int, Body(ge=1000, le=9999, embed=True)],
    current_user: UserCacheModel = Depends(get_current_unverified_user),
    session: AsyncSession = Depends(get_db_session),
):
    return await Container.auth_service.check_verification_code(
        code,
        current_user,
        session,
    )


@router.post(
    '/refresh-token',
    response_model=JWTResponse,
    summary='Refresh Token',
    description='Endpoint for refresh access token by refresh_token',
)
async def refresh_access_token(
    refresh_token: Annotated[str, Body(embed=True)],
    session: AsyncSession = Depends(get_db_session),
):
    return await Container.auth_service.refresh_access_token(
        refresh_token,
        session,
    )


@router.post(
    '/sign-in',
    response_model=JWTResponse,
    summary='Sign in',
    description='Endpoint for user login by email and password',
)
async def sign_in(
    request_schema: SignInRequest,
    session: AsyncSession = Depends(get_db_session),
):
    return await Container.auth_service.sign_in(
        request_schema,
        session,
    )
