#config.py
import os
from dotenv import load_dotenv
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base  # Import the Base from models.py

load_dotenv()

POSTGRES_URI = os.environ["POSTGRES_URI"]

engine = create_async_engine(POSTGRES_URI, echo=True, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def sync_init_db(conn):
    inspector = inspect(conn)
    for table in Base.metadata.sorted_tables:
        if not inspector.has_table(table.name):
            table.create(bind=conn, checkfirst=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(sync_init_db)
