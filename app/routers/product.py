from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update
from slugify import slugify

from typing import Annotated

from app.backend.db_depends import get_db
from app.models.products import Product
from app.models.category import Category
from app.schemas import CreateProduct

router = APIRouter(prefix='/products', tags=['продукты'])


@router.get('/all')
async def all_products(db_session: Annotated[Session, Depends(get_db)]):
    products = db_session.scalars(select(Product).where(Product.is_active == True, Product.stock > 0)).all()
    return products


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_product(db_session: Annotated[Session, Depends(get_db)], new_product: CreateProduct) -> dict:
    category = db_session.scalar(select(Category).where(Category.id == new_product.category))
    get_or_404(category)  # проверка существует ли объект данной категории
    stmt = insert(Product).values(name=new_product.name,
                                  slug=slugify(new_product.name),
                                  description=new_product.description,
                                  price=new_product.price,
                                  image_url=new_product.image_url,
                                  stock=new_product.stock,
                                  category_id=new_product.category,
                                  rating=0.0
                                  )
    db_session.execute(stmt)
    db_session.commit()
    return {'status': status.HTTP_201_CREATED, 'transaction': 'успешно'}


@router.get('/{category_slug}')
async def get_product_by_category(db_session: Annotated[Session, Depends(get_db)], category_slug: str):
    category = db_session.scalar(select(Category).where(Category.slug == category_slug))
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='категория не найдена')

    sub_categories = db_session.scalars(select(Category).where(Category.parent_id == category.id)).all()
    categories_id = [category.id for category in ([category] + sub_categories)]
    all_product_by_category = db_session.scalars(select(Product).where(Product.is_active == True,
                                                                       Product.stock > 0,
                                                                       Product.category_id.in_(categories_id))).all()
    if all_product_by_category:
        return all_product_by_category
    else:
        return 'Нет товаров данной категории'


@router.get('/detail/{product_slug}', status_code=status.HTTP_200_OK)
async def detail_product(db_session: Annotated[Session, Depends(get_db)], product_slug: str):
    product = db_session.scalar(select(Product).where(Product.slug == product_slug, Product.is_active == True))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Продукт с данным SLUG не найден')
    return product


@router.put('/{product_slug}', status_code=status.HTTP_200_OK)
async def update_product(db_session: Annotated[Session, Depends(get_db)],
                         product_slug: str,
                         update_product: CreateProduct) -> dict:
    product = db_session.scalar(select(Product).where(Product.slug == product_slug))
    get_or_404(product)
    db_session.execute(update(Product).where(Product.slug == product_slug).values(name=update_product.name,
                                                                                  slug=slugify(update_product.name),
                                                                                  description=update_product.description,
                                                                                  price=update_product.price,
                                                                                  image_url=update_product.image_url,
                                                                                  stock=update_product.stock,
                                                                                  category_id=update_product.category,
                                                                                  rating=0.0
                                                                                  ))
    db_session.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'Обновление продукта произошло успешно'}


@router.delete('/{product_slug}', status_code=status.HTTP_200_OK)
def delete_product(session_db: Annotated[Session, Depends(get_db)], product_slug: str):
    product = session_db.scalar(select(Product).where(Product.slug == product_slug))
    get_or_404(product)
    session_db.execute(update(Product).where(Product.slug == product_slug).values(is_active=False))
    session_db.commit()
    return dict(status_code=status.HTTP_200_OK, detail='Продукт успешно удален')


def get_or_404(items: Product | Category | list) -> None:
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Не найдено наименований с данным slug')
