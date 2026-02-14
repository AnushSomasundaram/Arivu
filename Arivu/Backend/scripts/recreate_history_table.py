
import asyncio
from sqlalchemy import text
from app.db.session import engine, init_db
from app.db.models import Base

async def recreate_table():
    print("Dropping chat_messages table...")
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS chat_messages"))
        
    print("Re-creating tables...")
    await init_db()
    print("Done.")

if __name__ == "__main__":
    asyncio.run(recreate_table())
