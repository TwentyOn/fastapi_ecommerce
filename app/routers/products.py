from typing import Annotated
from itertools import chain

from app.models.products import Product
from app.models.category import Category
from app.backend.db_depends import get_db
from app.schemas import CreateProduct

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update
from slugify import slugify

router = APIRouter(prefix='/products', tags=['Продукты'])


@router.get('/')
async def get_all_products(db: Annotated[Session, Depends(get_db)]):
    all_products = db.scalars(select(Product).where(Product.is_active == True, Product.stock >= 1)).all()
    if not all_products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Продукт не найден')
    return all_products


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_product(db: Annotated[Session, Depends(get_db)], create_product: CreateProduct) -> dict:
    category = db.scalar(select(Category).where(Category.id == create_product.category))
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Некорректная категория товара')
    db.execute(insert(Product).values(name=create_product.name,
                                      slug=slugify(create_product.name),
                                      description=create_product.description,
                                      price=create_product.price,
                                      rating=0.0,
                                      image_url=create_product.image_url,
                                      stock=create_product.stock,
                                      category_id=create_product.category))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transactions': 'Продукт успешно добавлен'}


@router.get('/{category_slug}')
async def get_product_by_category(db: Annotated[Session, Depends(get_db)], category_slug: str):
    category = db.scalar(select(Category).where(Category.slug == category_slug))
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")
    subcategory = db.scalars(select(Category).where(Category.parent_id == category.id)).all()
    category_and_subcategory = [category.id] + [item.id for item in subcategory]
    products_by_category = db.scalars(select(Product).where(Product.category_id.in_(category_and_subcategory))).all()
    return products_by_category


@router.get('/detail/{product_slug}')
async def get_product(db: Annotated[Session, Depends(get_db)], product_slug: str):
    product = db.scalar(select(Product).where(Product.slug == product_slug))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Продукт не найден')
    return product


@router.put('update/{product_slug}')
async def update_product_info(db: Annotated[Session, Depends(get_db)], product_slug: str,
                              update_product: CreateProduct) -> dict:
    product = db.scalar(select(Product).where(Product.slug == product_slug))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Продукт не найден')
    db.execute(update(Product).where(Product.slug == product_slug).values(name=update_product.name,
                                                                          description=update_product.description,
                                                                          price=update_product.price,
                                                                          image_url=update_product.image_url,
                                                                          stock=update_product.stock,
                                                                          category_id=update_product.category,
                                                                          slug=slugify(update_product.name)))
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transactions': 'Обновление успешно'}


@router.delete('delete/{product_slug}')
async def delete_product(db: Annotated[Session, Depends(get_db)], product_slug: str) -> dict:
    product = db.scalar(select(Product).where(Product.slug == product_slug))
    if not product:
        raise HTTPException('Продукт не найден')
    db.execute(update(Product).where(Product.slug == product_slug).values(is_active=False))
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transactions': 'Удаление успешно'}
