from app.backend.db import Base
from sqlalchemy import Column, Integer, String, Boolean, Float

a = 5
class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    description = Column(String)
    price = Column(Integer)
    image_url = Column(String)
    stock = Column(Integer)
    is_active = Column(Boolean, default=True)