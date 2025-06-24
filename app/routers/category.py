from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import insert, delete, select, update
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify

from typing import Annotated

from app.backend.db_depends import get_db
from app.models.category import Category
from app.schemas import CreateCategory

router = APIRouter(prefix='/categories', tags=['категории'])


@router.get('/all')
async def get_all_categories(db_session: Annotated[AsyncSession, Depends(get_db)]):
    all_categories = await db_session.scalars(select(Category).where(Category.is_active))
    return all_categories.all()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_category(db_session: Annotated[AsyncSession, Depends(get_db)], category: CreateCategory) -> dict:
    stmt = insert(Category).values(name=category.name, slug=slugify(category.name), parent_id=category.parent_id)
    await db_session.execute(stmt)
    await db_session.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Успешно'}


@router.put('/{category_slug}')
async def update_category(db_session: Annotated[AsyncSession, Depends(get_db)], category_slug: str,
                          update_category: CreateCategory) -> dict:
    category_to_update = await db_session.scalar(select(Category)
                                                 .where(Category.slug == category_slug, Category.is_active == True))

    if not category_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Нет активных категорий с данным SLUG')

    category_to_update.name = update_category.name
    category_to_update.slug = slugify(update_category.name)
    category_to_update.parent_id = update_category.parent_id
    await db_session.commit()
    return {'status_code': status.HTTP_200_OK, 'message': 'Обновление успешно'}


@router.delete('/{category_slug}')
async def delete_category(db_session: Annotated[Session, Depends(get_db)], category_slug: str) -> dict:
    category_to_delete = await db_session.scalar(
        select(Category).where(Category.slug == category_slug, Category.is_active == True))
    if not category_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Нет активных категорий с данным SLUG')

    category_to_delete.is_active = False
    await db_session.commit()
    return {'status_code': status.HTTP_200_OK, 'message': 'удаление успешно'}
