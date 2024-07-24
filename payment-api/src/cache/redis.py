from redis.asyncio import Redis

client: Redis | None = None


async def get_cache() -> Redis:
    return client
