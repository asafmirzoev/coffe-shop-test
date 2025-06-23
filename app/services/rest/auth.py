import datetime
import logging
import random

import argon2
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.environment import env
from app.cache.models.user import UserCacheModel
from app.core.exceptions import (
    raise_exception,
    DuplicateException,
    ErrorMessageCodes,
    BadRequestException,
    PermissionDeniedException,
)
from app.db.exceptions import DbObjectDoesNotExist
from app.db.models.user import UserDbModel
from app.schemas.rest.auth import (
    SignUpRequest,
    JwtTokenPayload,
    JWTResponse,
    SignInRequest,
)
from app.services import BaseService


class AuthService(BaseService):
    """
    Service for processing requests from router 'rest/auth'
    """

    async def sign_up(
        self,
        request_schema: SignUpRequest,
        session: AsyncSession,
    ) -> JWTResponse:
        """
        Service method for processing the request ‘/rest/sign-up’
        """

        if await self.container.user_db_repo.exists(
            request_schema.email,
            session=session,
        ):
            raise raise_exception(
                DuplicateException,
                ErrorMessageCodes.EMAIL_ALREADY_REGISTERED,
            )

        try:
            password_hash = self.container.password_hasher.hash(request_schema.password)
        except argon2.exceptions.HashingError:
            raise raise_exception(
                BadRequestException,
                ErrorMessageCodes.BAD_PASSWORD,
            )

        # Упростил назначение админа
        user_db_model = UserDbModel(
            email=request_schema.email,
            first_name=request_schema.first_name,
            last_name=request_schema.last_name,
            password=password_hash,
            is_admin=request_schema.email == env.admin_email.get_secret_value(),
        )
        user_cache_model = await self.container.user_union.create(
            user_db_model,
            session=session,
        )

        verification_code = random.randint(1000, 9999)
        logging.warning(f'Verification code: {verification_code}')
        # FIXME: I could put the sending of code on a queue, like kafka or redis pubsub

        await self.container.user_cache_repo.set_verification_code(
            user_cache_model.id,
            verification_code,
        )

        return await self._generate_jwt_response(user_cache_model)

    async def resend_verification_code(
        self,
        current_user: UserCacheModel,
    ) -> None:
        """
        Service method for processing the request ‘/rest/resend-verification-code’
        """

        if await self.container.user_cache_repo.check_verification_code_limit(
            current_user.id
        ):
            raise raise_exception(
                PermissionDeniedException,
                ErrorMessageCodes.VERIFICATION_CODE_LIMIT,
            )

        # FIXME: I could add more checking for the number of ‘sms’ sent recently, but that would take more time :)

        verification_code = random.randint(1000, 9999)
        logging.warning(f'Verification code: {verification_code}')

        await self.container.user_cache_repo.set_verification_code(
            current_user.id,
            verification_code,
        )

    async def check_verification_code(
        self,
        code: int,
        current_user: UserCacheModel,
        session: AsyncSession,
    ) -> JWTResponse:
        """
        Service method for processing the request ‘/rest/check-verification-code’
        """

        # FIXME: I could add more checking for the number of code check requests recently, but that would take more time :)

        verified = await self.container.user_cache_repo.check_verification_code(
            current_user.id,
            code=code,
        )
        if not verified:
            raise raise_exception(
                PermissionDeniedException,
                ErrorMessageCodes.INVALID_CODE,
            )

        current_user.verified = True
        await self.container.user_union.update(
            current_user,
            values={
                'verified': verified,
            },
            session=session,
        )

        return await self._generate_jwt_response(
            current_user,
            with_refresh_token=True,
        )

    async def refresh_access_token(
        self,
        refresh_token: str,
        session: AsyncSession,
    ) -> JWTResponse:
        try:
            payload = jwt.decode(
                refresh_token,
                env.jwt_secretkey.get_secret_value(),
                algorithms=[env.jwt_algorithm],
            )
        except Exception:
            raise raise_exception(
                PermissionDeniedException,
                ErrorMessageCodes.INVALID_REFRESH_TOKEN,
            )

        token_type = payload.get('type', None)
        if token_type != 'refresh':
            raise raise_exception(
                PermissionDeniedException,
                ErrorMessageCodes.INVALID_REFRESH_TOKEN,
            )
        user_id = int(payload['id'])

        try:
            user_cache_model = await self.container.user_union.get(
                user_id,
                session=session,
            )
        except DbObjectDoesNotExist:
            raise raise_exception(
                PermissionDeniedException,
                ErrorMessageCodes.USER_NOT_FOUND,
            )

        return await self._generate_jwt_response(user_cache_model)

    async def sign_in(
        self,
        request_schema: SignInRequest,
        session: AsyncSession,
    ) -> JWTResponse:
        try:
            user_cache_model = await self.container.user_union.get_by_email(
                request_schema.email,
                session=session,
            )
        except DbObjectDoesNotExist:
            raise raise_exception(
                PermissionDeniedException,
                ErrorMessageCodes.INVALID_EMAIL_OR_PASSWORD,
            )

        password_verified = await self.container.user_union.verify_password(
            user_cache_model.id,
            request_schema.password,
            session=session,
        )
        if not password_verified:
            raise raise_exception(
                PermissionDeniedException,
                ErrorMessageCodes.INVALID_EMAIL_OR_PASSWORD,
            )

        return await self._generate_jwt_response(
            user_cache_model,
            with_refresh_token=True,
        )

    @staticmethod
    async def _generate_jwt_response(
        user_cache_model: UserCacheModel,
        with_refresh_token: bool = False,
    ) -> JWTResponse:
        now = datetime.datetime.now(datetime.UTC)

        access_token_exp = now + datetime.timedelta(
            minutes=env.access_token_lifetime,
        )
        token_payload = JwtTokenPayload(
            id=user_cache_model.id,
            type='access',
            exp=access_token_exp,
        )
        access_token = jwt.encode(
            token_payload.model_dump(),
            env.jwt_secretkey.get_secret_value(),
            algorithm=env.jwt_algorithm,
        )

        refresh_token = None
        if with_refresh_token:
            refresh_token_exp = now + datetime.timedelta(
                minutes=env.refresh_token_lifetime,
            )
            token_payload = JwtTokenPayload(
                id=user_cache_model.id,
                type='refresh',
                exp=refresh_token_exp,
            )
            refresh_token = jwt.encode(
                token_payload.model_dump(),
                env.jwt_secretkey.get_secret_value(),
                algorithm=env.jwt_algorithm,
            )

        return JWTResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires=access_token_exp,
        )
