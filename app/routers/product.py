from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from slugify import slugify

from typing import Annotated

from app.backend.db_depends import get_db
from app.models.products import Product
from app.models.category import Category
from app.schemas import CreateProduct
from app.routers.auth import get_current_user

router = APIRouter(prefix='/products', tags=['продукты'])


@router.get('/all')
async def all_products(db_session: Annotated[AsyncSession, Depends(get_db)]):
    products = await db_session.scalars(select(Product).where(Product.is_active == True, Product.stock > 0))
    return products.all()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_product(db_session: Annotated[AsyncSession, Depends(get_db)], new_product: CreateProduct,
                         get_user: Annotated[dict, Depends(get_current_user)]) -> dict:
    if not any([get_user.get(i) for i in ('is_admin', 'is_supplier')]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')
    category = await db_session.scalar(select(Category).where(Category.id == new_product.category))
    get_or_404(category)  # проверка существует ли объект данной категории
    stmt = insert(Product).values(name=new_product.name,
                                  slug=slugify(new_product.name),
                                  description=new_product.description,
                                  price=new_product.price,
                                  image_url=new_product.image_url,
                                  stock=new_product.stock,
                                  category_id=new_product.category,
                                  rating=0.0,
                                  supplier_id=get_user.get('user_id')
                                  )
    await db_session.execute(stmt)
    await db_session.commit()
    return {'status': status.HTTP_201_CREATED, 'transaction': 'успешно'}


@router.get('/{category_slug}')
async def get_product_by_category(db_session: Annotated[AsyncSession, Depends(get_db)], category_slug: str):
    category = await db_session.scalar(select(Category).where(Category.slug == category_slug))
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='категория не найдена')

    sub_categories = await db_session.scalars(select(Category).where(Category.parent_id == category.id))
    categories_id = [category.id for category in ([category] + sub_categories.all())]
    all_product_by_category = await db_session.scalars(select(Product).where(Product.is_active == True,
                                                                             Product.stock > 0,
                                                                             Product.category_id.in_(categories_id)))
    if all_product_by_category:
        return all_product_by_category.all()
    else:
        return 'Нет товаров данной категории'


@router.get('/detail/{product_slug}', status_code=status.HTTP_200_OK)
async def detail_product(db_session: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db_session.scalar(select(Product).where(Product.slug == product_slug, Product.is_active == True))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Продукт с данным SLUG не найден')
    return product


@router.put('/{product_slug}', status_code=status.HTTP_200_OK)
async def update_product(db_session: Annotated[AsyncSession, Depends(get_db)],
                         product_slug: str,
                         update_product: CreateProduct,
                         get_user: Annotated[dict, Depends(get_current_user)]) -> dict:
    product = await db_session.scalar(select(Product).where(Product.slug == product_slug))
    get_or_404(product)

    if not any([get_user.get(i) for i in ('is_admin', 'is_supplier')]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')
    if get_user.get('is_supplier'):
        if product.supplier_id != get_user.get('user_id'):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='У вас нет прав изменять данный товар')

    product.name = update_product.name
    product.slug = slugify(update_product.name)
    product.description = update_product.description
    product.price = update_product.price
    product.image_url = update_product.image_url
    product.stock = update_product.stock
    product.category_id = update_product.category

    await db_session.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'Обновление продукта произошло успешно'}


@router.delete('/{product_slug}', status_code=status.HTTP_200_OK)
async def delete_product(db_session: Annotated[AsyncSession, Depends(get_db)], product_slug: str,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    product = await db_session.scalar(select(Product).where(Product.slug == product_slug))
    get_or_404(product)

    if not any([get_user.get(i) for i in ('is_admin', 'is_supplier')]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')
    if get_user.get('is_supplier') and product.supplier_id != get_user.get('user_id'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='У вас нет прав изменять данный товар')

    product.is_active = False
    await db_session.commit()
    return dict(status_code=status.HTTP_200_OK, detail='Продукт успешно удален')


def get_or_404(items: Product | Category | list) -> None:
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Не найдено наименований с данным slug')
