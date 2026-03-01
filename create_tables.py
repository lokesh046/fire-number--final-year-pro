import asyncio

from shared.database import engine, Base

# 🔥 IMPORTANT – import ALL models so SQLAlchemy registers them
from shared.models import user
from shared.models import financial_profile
from shared.models import fire
from shared.models import health
from shared.models import loan
from shared.models import chat


async def create():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(create())