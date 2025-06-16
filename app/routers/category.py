from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import insert, delete, select, update
from sqlalchemy.orm import Session
from slugify import slugify

from typing import Annotated

from app.backend.db_depends import get_db
from app.models.category import Category
from app.schemas import CreateCategory

router = APIRouter(prefix='/categories', tags=['категории'])


@router.get('/all')
async def get_all_categories(db_session: Annotated[Session, Depends(get_db)]):
    all_categories = db_session.scalars(select(Category)).all()
    return all_categories


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_category(db_session: Annotated[Session, Depends(get_db)], category: CreateCategory) -> dict:
    smtm = insert(Category).values(name=category.name, slug=slugify(category.name), parent_id=category.parent_id)
    db_session.execute(smtm)
    db_session.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router.put('/{category_slug}')
async def update_category(category_slug: str) -> str:
    pass


@router.delete('/{category_slug}')
async def delete_category(db_session: Annotated[Session, Depends(get_db)], category_slug: str) -> str:
    category_to_delete = db_session.scalar(
        select(Category).where(Category.slug == category_slug, Category.is_active == True))
    if not category_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Нет активных категорий с данным SLUG')
    else:
        db_session.execute(
            update(Category).where(Category.slug == category_slug, Category.is_active == True).values(is_active=False))
    db_session.commit()
    return 'Категория успешно удалена'
