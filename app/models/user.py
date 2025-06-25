from sqlalchemy import Column, Integer, String, Boolean
from app.backend.db import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    lastname = Column(String)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_customer = Column(Boolean, default=True)
    is_supplier = Column(Boolean, default=False)
