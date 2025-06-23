from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(BaseSettings):
    debug: bool = False

    # Admin
    admin_email: SecretStr

    # JWT
    jwt_algorithm: str
    jwt_secretkey: SecretStr
    access_token_lifetime: int
    refresh_token_lifetime: int

    # Database
    db_connection: SecretStr

    # Redis
    redis_host: str
    redis_port: int
    redis_username: Optional[SecretStr] = None
    redis_password: Optional[SecretStr] = None
    redis_ssl: bool = False

    pagination_items: int = 30

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


env = Environment()
