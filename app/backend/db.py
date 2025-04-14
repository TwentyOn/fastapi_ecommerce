from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

engine = create_engine('sqlite:///ecommerce.db', echo=True) # движок sqlalchemy
session_local = sessionmaker(bind=engine) # сессия базы данных для CRUD-функционала


class Base(DeclarativeBase):
    '''Базовый класс для создания моделей баз данных'''
    pass
