"""
Redis connection management and sliding window rate limiter.
"""

import time
from typing import Tuple
from app.config import settings
from app.models.project import AccessTier

try:
    import redis.asyncio as aioredis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

# Fallback in-memory rate limit store for offline/testing development
_in_memory_rate_store = {}


class RateLimiter:
    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis_url = redis_url
        self.redis = None

    async def init_redis(self):
        if HAS_REDIS and self.redis_url:
            try:
                self.redis = aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
                await self.redis.ping()
            except Exception:
                self.redis = None

    async def check_rate_limit(
        self, project_id: str, tier: AccessTier, feature: str = "contract"
    ) -> Tuple[bool, int, int]:
        """
        Checks monthly rate limit for a project tier.
        
        Returns:
            Tuple[is_allowed, current_usage, limit]
        """
        # Determine limit based on tier
        if feature == "contract":
            limit_map = {
                AccessTier.DEVELOPER: settings.LIMIT_DEVELOPER_CONTRACTS,
                AccessTier.BUILDER: settings.LIMIT_BUILDER_CONTRACTS,
                AccessTier.PROTOCOL: settings.LIMIT_PROTOCOL_CONTRACTS,
                AccessTier.ENTERPRISE: -1,
            }
        else:
            limit_map = {
                AccessTier.DEVELOPER: settings.LIMIT_DEVELOPER_ADDRESSES,
                AccessTier.BUILDER: settings.LIMIT_BUILDER_ADDRESSES,
                AccessTier.PROTOCOL: settings.LIMIT_PROTOCOL_ADDRESSES,
                AccessTier.ENTERPRISE: -1,
            }

        limit = limit_map.get(tier, 50)
        if limit == -1:
            return True, 0, -1  # Unlimited

        current_month = time.strftime("%Y-%m")
        key = f"rate_limit:{project_id}:{feature}:{current_month}"

        if self.redis:
            try:
                current_usage = await self.redis.incr(key)
                if current_usage == 1:
                    # Expire at end of month (~31 days)
                    await self.redis.expire(key, 31 * 86400)
                is_allowed = current_usage <= limit
                return is_allowed, current_usage, limit
            except Exception:
                pass  # Fall back to in-memory

        # In-memory fallback
        current_usage = _in_memory_rate_store.get(key, 0) + 1
        _in_memory_rate_store[key] = current_usage
        is_allowed = current_usage <= limit
        return is_allowed, current_usage, limit


rate_limiter = RateLimiter()
