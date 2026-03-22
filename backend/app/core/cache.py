"""缓存管理"""
import json
from typing import Optional, Any
import redis.asyncio as redis
from ..config import REDIS_URL, DATA_CACHE_TTL

class CacheManager:
    """Redis 缓存管理器"""

    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._ttl = DATA_CACHE_TTL

    async def connect(self):
        """连接 Redis"""
        if not self._client:
            self._client = redis.from_url(REDIS_URL, decode_responses=True)

    async def disconnect(self):
        """断开连接"""
        if self._client:
            await self._client.close()
            self._client = None

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not self._client:
            return None
        value = await self._client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, ttl: int = None):
        """设置缓存"""
        if not self._client:
            return
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self._client.set(key, value, ex=ttl or self._ttl)

    async def delete(self, key: str):
        """删除缓存"""
        if self._client:
            await self._client.delete(key)

    async def clear_pattern(self, pattern: str):
        """清除匹配的缓存"""
        if self._client:
            keys = await self._client.keys(pattern)
            if keys:
                await self._client.delete(*keys)


# 全局缓存实例
cache = CacheManager()