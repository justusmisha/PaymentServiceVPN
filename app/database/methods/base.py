import asyncio

from app.core.config import AsyncSessionLocal


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session



