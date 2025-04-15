from typing import Annotated

from app.models.products import Product
from app.backend.db_depends import get_db
from app.schemas import CreateProduct

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import insert
from slugify import slugify

router = APIRouter(prefix='/products', tags=['Продукты'])


@router.get('/')
async def get_all_products() -> dict:
    pass


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_product(db: Annotated[Session, Depends(get_db)], create_product: CreateProduct):
    db.execute(insert(Product).values(name=create_product.name,
                                      slug=slugify(create_product.name),
                                      description=create_product.description,
                                      ))


@router.get('/{category_slug}')
async def get_product_by_category(category_slug: str) -> dict:
    pass


@router.get('/detail/{product_slug}')
async def get_product(product_slug: str):
    pass


@router.put('update/{product_slug}')
async def update_product_info(product_slug: str) -> str:
    pass


@router.delete('delete/{product_slug}')
async def delete_product(product_slug: str) -> str:
    pass
