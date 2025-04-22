from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db import async_sessions_maker

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_sessions_maker as async_session:
        yield async_session