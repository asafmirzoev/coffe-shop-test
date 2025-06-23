from typing import Optional

from redis.asyncio import ConnectionPool, Redis


async def get_redis_client(
    redis_host: str,
    redis_port: int,
    redis_username: Optional[str],
    redis_password: Optional[str],
    redis_ssl: bool,
):
    if redis_ssl:
        protocol = 'rediss'
    else:
        protocol = 'redis'

    pool: ConnectionPool = ConnectionPool.from_url(
        f'{protocol}://{redis_username}:{redis_password}@{redis_host}:{redis_port}?decode_responses=True',
        decode_responses=True,
    )
    redis_client = Redis(
        connection_pool=pool,
        decode_responses=True,
    )
    return redis_client
