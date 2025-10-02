import asyncio
from core.utils.database import AsyncDatabaseTool
from settings import settings

"""
    Scripts to run migration
"""


async def init_models():
    conn = AsyncDatabaseTool(settings.database_url)
    print("Creating tables...")
    try:
        await conn.migration()
    except Exception as ex:
        print(f"Failed to migrate Database: {ex}")
    print("Finish creating tables...")

if __name__ == "__main__":
    asyncio.run(init_models())
