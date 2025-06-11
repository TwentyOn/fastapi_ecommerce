from app.backend.db import Base
from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.orm import Relationship
from app.models.products import Product


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    products = Relationship('Product', uselist=False, back_populates='category')

from sqlalchemy.schema import CreateTable

print(CreateTable(Category.__table__))
print(CreateTable(Product.__table__))