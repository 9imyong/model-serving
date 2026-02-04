# app/adapters/redis/idem_gate.py
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from redis.asyncio import Redis


def _idem_key(input_uri: str) -> str:
    h = hashlib.sha256(input_uri.encode("utf-8")).hexdigest()[:24]
    return f"idem:job:input_uri:{h}"


@dataclass(slots=True)
class RedisIdempotencyGate:
    redis: Redis
    ttl_sec: int = 3600

    @classmethod
    def from_env(cls, *, ttl_sec: int | None = None) -> RedisIdempotencyGate:
        url = os.getenv("REDIS_URL", "").strip()
        if not url:
            host = os.getenv("REDIS_HOST", "localhost")
            port = os.getenv("REDIS_PORT", "6379")
            url = f"redis://{host}:{port}/0"
        redis = Redis.from_url(url, decode_responses=True)
        return cls(redis=redis, ttl_sec=ttl_sec or 3600)

    async def reserve(self, input_uri: str, job_id: str) -> bool:
        key = _idem_key(input_uri)
        return bool(await self.redis.set(key, job_id, nx=True, ex=self.ttl_sec))

    async def get(self, input_uri: str) -> str | None:
        key = _idem_key(input_uri)
        val = await self.redis.get(key)
        return val if val else None
