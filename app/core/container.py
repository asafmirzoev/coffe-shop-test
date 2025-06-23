from argon2 import PasswordHasher
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.cache import get_redis_client
from app.cache.repos.user import UserCacheRepo
from app.cache.repos.users import UsersCacheRepo
from app.core.environment import env
from app.db.models import BaseDbModel
from app.db.repos.user import UserDbRepo
from app.unions.user import UserUnion


class Container:
    """
    The class is a 'container' that contains all the necessary application components that need to be accessed from anywhere in the application.
    It is initialised at application startup, and lives as long as the application is alive.
    This class is used as a singleton dependency throughout the application.
    """

    @classmethod
    async def initialize(cls):
        """
        Method for initialising components
        """

        cls.password_hasher = PasswordHasher()

        cls.__engine = create_async_engine(
            env.db_connection.get_secret_value(),
            echo=False,
        )
        cls.async_session = async_sessionmaker(
            bind=cls.__engine,
            expire_on_commit=False,
        )

        cls.redis_client = await get_redis_client(
            env.redis_host,
            env.redis_port,
            env.redis_username.get_secret_value() if env.redis_username else None,
            env.redis_password.get_secret_value() if env.redis_password else None,
            env.redis_ssl,
        )

        cls.user_db_repo = UserDbRepo()

        cls.user_cache_repo = UserCacheRepo(
            container=cls,
        )
        cls.users_cache_repo = UsersCacheRepo(
            container=cls,
        )

        cls.user_union = UserUnion(
            container=cls,
        )

    @classmethod
    async def initialize_services(cls):
        """
        Method for initialising services
        """

        from app.services.rest.auth import AuthService
        from app.services.rest.users import UsersService

        cls.auth_service = AuthService(
            container=cls,
        )
        cls.users_service = UsersService(
            container=cls,
        )

    @classmethod
    async def initialize_database(cls):
        """
        Method for initialising database
        """

        async with cls.__engine.begin() as conn:
            await conn.run_sync(BaseDbModel.metadata.create_all)
