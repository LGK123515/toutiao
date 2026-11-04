import asyncio

from config.db_config import async_engine
from models.ai import Base


async def create_table():
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    await async_engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_table())