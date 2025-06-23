import jwt
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.environment import env
from app.core.exceptions import UnauthorizedException


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == 'Bearer':
                raise UnauthorizedException(detail='Invalid authentication scheme.')
            if not self.verify_jwt(credentials.credentials):
                raise UnauthorizedException(detail='Invalid token or expired token.')
            return credentials.credentials
        else:
            raise UnauthorizedException(detail='Invalid authorization code.')

    @staticmethod
    def verify_jwt(jwt_token: str) -> bool:
        try:
            payload = jwt.decode(
                jwt_token,
                env.jwt_secretkey.get_secret_value(),
                algorithms=[env.jwt_algorithm],
            )
        except Exception:
            payload = None
        return bool(payload)
