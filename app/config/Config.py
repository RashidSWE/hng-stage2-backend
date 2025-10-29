import os
from dotenv import load_dotenv
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine ,AsyncSession
from sqlalchemy.orm import sessionmaker

""" Load environment variables"""
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

""" create engine """
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

""" create async session """
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

""" Initialize DB"""
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


