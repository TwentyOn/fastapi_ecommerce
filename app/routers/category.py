from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import insert
from app.backend.db_depends import get_db
from app.schemas import CreateCategory, CreateProduct
from app.models.category import Category
from slugify import slugify

from typing import Annotated

router = APIRouter(prefix='/categories', tags=['Категории'])


@router.get('/{category_name}/{category_id}')
async def get_all_categories() -> dict:
    pass


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_category(db: Annotated[Session, Depends(get_db)], create_category: CreateCategory) -> dict:
    db.execute(insert(Category).values(name=create_category.name,
                                       parent_id=create_category.parent_id,
                                       slug=slugify(create_category.name)))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED,
            'transaction': 'successful'}


@router.put('/')
async def update_category():
    pass


@router.delete('/')
async def delete_category():
    pass
