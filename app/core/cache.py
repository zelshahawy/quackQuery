from __future__ import annotations

import hashlib
import json
from typing import Any

import redis

from app.config import settings


def _get_redis_client() -> redis.Redis:
    """Get Redis client from settings."""
    return redis.from_url(settings.redis_url, decode_responses=True)


def _hash_query(question: str, table_name: str) -> str:
    """Create a hash of the question and table for cache key."""
    key = f"query:{question}:{table_name}"
    return hashlib.md5(key.encode()).hexdigest()


def get_cached_result(question: str, table_name: str) -> dict[str, Any] | None:
    """Get cached result if it exists."""
    try:
        client = _get_redis_client()
        cache_key = _hash_query(question, table_name)
        cached_data = client.get(cache_key)

        if cached_data:
            return json.loads(cached_data)
        return None
    except Exception as e:
        print(f"Cache get error: {e}")
        return None


def cache_result(
    question: str, table_name: str, sql: str, df_json: str, ttl: int = 3600
) -> None:
    """Cache a query result with TTL (default 1 hour)."""
    try:
        client = _get_redis_client()
        cache_key = _hash_query(question, table_name)

        data = {
            "question": question,
            "table_name": table_name,
            "sql": sql,
            "df_json": df_json,
        }

        client.setex(cache_key, ttl, json.dumps(data))
    except Exception as e:
        print(f"Cache set error: {e}")


def clear_cache() -> None:
    """Clear all cached results."""
    try:
        client = _get_redis_client()
        # Delete all keys matching our pattern
        for key in client.scan_iter("query:*"):
            client.delete(key)
    except Exception as e:
        print(f"Cache clear error: {e}")
