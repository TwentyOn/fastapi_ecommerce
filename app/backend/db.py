from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

#engine = create_engine('sqlite:///ecommerce.db', echo=True)  # движок sqlite sqlalchemy
#session_local = sessionmaker(bind=engine)  # фабрика сессий базы данных для CRUD-функционала

engine = create_async_engine('postgresql+asyncpg://ecommerce:643941@localhost:5432/ecommerce', echo=True)
async_sessions_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    '''Базовый класс для создания моделей баз данных'''
    pass
