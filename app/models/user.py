from sqlalchemy import Column, Integer, String, Boolean
from app.backend.db import Base

class User(Base):
    __tablename__= 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    lastname = Column(String)
    username = Column(String, unique=True)
    email = Column(String)
