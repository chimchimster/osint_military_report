from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from .engine import ms_engine

LocalAsyncSession = sessionmaker(
    ms_engine.engine, class_=AsyncSession, expire_on_commit=False,
)
