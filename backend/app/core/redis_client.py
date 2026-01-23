import json
from typing import Any, Optional
from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import RedisError
from app.core.config import settings

# redis connection pool
redis_pool = ConnectionPool.from_url(
    settings.redis_url,
    max_connections=10,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30
)

# redis client
async def get_redis() -> Redis:
    return Redis(connection_pool=redis_pool)

class RedisCache:
    def __init__(self):
        self.redis: Optional[Redis] = None
    
    async def connect(self) -> None:
        self.redis = await get_redis()

    async def close(self) -> None:
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Optional[str]:
        try:
            return await self.redis.get(key)
        except RedisError as e:
            print(f"Redis GET error: {e}")
            return None
    
    async def set(
            self,
            key: str,
            value: str,
            ttl: Optional[int] = None
    ) -> bool:
        try:
            if ttl:
                await self.redis.setex(key, ttl, value)
            else:
                await self.redis.set(key, value)
            return True
        except RedisError as e:
            print(f"Redis SET error: {e}")
            return False
        
    async def get_json(self, key: str) -> Optional[dict]:
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def set_json(
        self,
        key: str,
        value: dict,
        ttl: Optional[int] = None
    ) -> bool:
        try:
            json_str = json.dumps(value)
            return await self.set(key, json_str, ttl)
        except (TypeError, json.JSONEncodeError) as e:
            print(f"JSON serialization error: {e}")
            return False
        
    async def delete(self, key: str) -> bool:
        try:
            result = await self.redis.delete(key)
            return result > 0
        except RedisError as e:
            print(f"Redis DELETE error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        try:
            return await self.redis.exists(key) > 0
        except RedisError as e:
            print(f"Redis EXISTS error: {e}")
            return False
        
    async def expire(self, key: str, ttl: int) -> bool:
        try:
            return await self.redis.expire(key, ttl)
        except RedisError as e:
            print(f"Redis EXPIRE error: {e}")
            return False
        
    async def ttl(self,  key:str) -> int:
        try:
            return await self.redis.ttl(key)
        except RedisError as e:
            print(f"Redis TTL error: {e}")
            return -2  # key does not exist
        
    async def increment(self, key: str, amount: int =1) -> int:
        try:
            return await self.redis.incrby(key, amount)
        except RedisError as e:
            print(f"Redis INCRBY error: {e}")
            return 0
        
    async def delete_pattern(self, pattern: str) -> int:
        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                return await self.redis.delete(*keys)
            return 0
        except RedisError as e:
            print(f"Redis DELETE_PATTERN error: {e}")
            return 0

# singleton redis cache instance
cache = RedisCache()

async def init_redis() -> None:
    await cache.connect()
    print("Connected to Redis")

async def close_redis() -> None:
    await cache.close()
    print("Disconnected from Redis")

async def store_refresh_token(user_id: str, token: str) -> bool:
    key = f"refresh_token:{user_id}"
    ttl = settings.refresh_token_expire_days * 86400
    return await cache.set(key, token, ttl=ttl)

async def get_refresh_token(user_id: str) -> Optional[str]:
    key = f"refresh_token:{user_id}"
    return await cache.get(key)

async def revoke_refresh_token(user_id: str) -> bool:
    key = f"refresh_token:{user_id}"
    return await cache.delete(key)

# helpers for stats caching
def get_stats_chache_key(user_id: str, stat_type:str) -> str:
    return f"stats:{user_id}:{stat_type}"

async def invalidate_user_stats(user_id: str) -> int:
    pattern = f"stats:{user_id}:*"
    return await cache.delete_pattern(pattern)