"""Worker readiness probe script for container exec checks.

Exits 0 when database and Redis respond; exits 1 otherwise.
Does not import application health services to avoid coupling to business wiring.
"""

from __future__ import annotations

import asyncio
import os
import sys


async def _check() -> bool:
    database_url = os.environ.get("CCH_DATABASE_URL")
    redis_url = os.environ.get("CCH_REDIS_URL")
    if not database_url or not redis_url:
        return False

    try:
        import asyncpg
        import redis.asyncio as redis
    except ImportError:
        return False

    conn = await asyncpg.connect(database_url.replace("postgresql+asyncpg://", "postgresql://"))
    try:
        await conn.execute("SELECT 1")
    finally:
        await conn.close()

    client = redis.from_url(str(redis_url))
    try:
        pong = await client.ping()
    finally:
        await client.aclose()
    return bool(pong)


def main() -> int:
    ok = asyncio.run(_check())
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
