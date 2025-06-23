from enum import Enum
from typing import Any, Optional

from fastapi import HTTPException, status


class UnauthorizedException(HTTPException):
    def __init__(
        self, detail: Any = None, headers: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, headers)


class PermissionDeniedException(HTTPException):
    def __init__(
        self, detail: Any = None, headers: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)


class NotFoundException(HTTPException):
    def __init__(
        self, detail: Any = None, headers: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class BadRequestException(HTTPException):
    def __init__(
        self, detail: Any = None, headers: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class DuplicateException(HTTPException):
    def __init__(
        self, detail: Any = None, headers: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(status.HTTP_409_CONFLICT, detail, headers)


class ErrorMessageCodes(str, Enum):
    AUTH_FAILED = 'AUTH_FAILED'
    EMAIL_ALREADY_REGISTERED = 'EMAIL_ALREADY_REGISTERED'
    BAD_PASSWORD = 'BAD_PASSWORD'
    USER_NOT_FOUND = 'USER_NOT_FOUND'
    USER_ALREADY_VERIFIED = 'USER_ALREADY_VERIFIED'
    VERIFICATION_CODE_LIMIT = 'VERIFICATION_CODE_LIMIT'
    INVALID_CODE = 'INVALID_CODE'
    INVALID_REFRESH_TOKEN = 'INVALID_REFRESH_TOKEN'
    INVALID_EMAIL_OR_PASSWORD = 'INVALID_EMAIL_OR_PASSWORD'


def raise_exception(
    exception_class,
    error_code: ErrorMessageCodes,
):
    return exception_class({'error_code': error_code.value})
