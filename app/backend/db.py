from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import dotenv, os

config = dotenv.dotenv_values('D://PycharmProjects/LearnFastAPI/app/migrations/.env')
POSTGRES_USER = config["POSTGRES_USER"]
POSTGRES_PASSWORD = config['POSTGRES_PASSWORD']
POSTGRES_DB = config['POSTGRES_DB']

engine = create_async_engine(f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}', echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


"""
Движок и фабрика сессий на основе sqlite

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

engine = create_engine('sqlite:///ecommerce.db', echo=True)
SessionLocal = sessionmaker(bind=engine)
"""
