from typing import Annotated

from app.backend.db_depends import get_db
from app.schemas import CreateCategory, CreateProduct
from app.models.category import Category

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update
from slugify import slugify

router = APIRouter(prefix='/categories', tags=['Категории'])


@router.get('/')
async def get_all_categories(db: Annotated[Session, Depends(get_db)]):
    categories = db.scalars(select(Category).where(Category.is_active == True)).all()
    return categories


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_category(db: Annotated[Session, Depends(get_db)], create_category: CreateCategory) -> dict:
    db.execute(insert(Category).values(name=create_category.name,
                                       parent_id=create_category.parent_id,
                                       slug=slugify(create_category.name)))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED,
            'transaction': 'successful'}


@router.put('/{category_slug}')
async def update_category(db: Annotated[Session, Depends(get_db)], category_slug: str, update_category: CreateCategory):
    category = db.scalar(select(Category).where(Category.slug == category_slug))
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Записи с данным slug не найдено')

    db.execute(update(Category).where(Category.slug == category_slug).values(name=update_category.name,
                                                                             slug=slugify(update_category.name),
                                                                             parent_id=update_category.parent_id))
    db.commit()
    return {'status': status.HTTP_200_OK, 'transaction': f'Запись обновлена'}


@router.delete('/{category_slug}')
async def delete_category(db: Annotated[Session, Depends(get_db)], category_slug: str):
    category = db.scalar(select(Category).where(Category.slug == category_slug, Category.is_active == True))
    if not category:
        raise HTTPException(status_code=404, detail='категория не найдена')
    db.execute(update(Category).where(Category.slug == category_slug).values(is_active=False))
    db.commit()
    return {'status': status.HTTP_200_OK, 'transaction': "Удаление успешно"}
