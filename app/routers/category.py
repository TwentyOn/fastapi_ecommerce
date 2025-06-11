from fastapi import APIRouter, Depends
from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.backend.db_depends import get_db
from app.models.category import Category
from app.schemas import CreateCategory
from typing import Annotated

router = APIRouter(prefix='/categories', tags=['категории'])


@router.get('/all')
async def get_all_categories() -> str:
    return 'пока нет категорий'


@router.post('/all')
async def create_category(db_session: Annotated[Session, Depends(get_db)], category: CreateCategory) -> str:
    smtm = insert(Category).values(name=category.name, slug=category.name, parent_id=category.parent_id)
    db_session.execute(smtm)
    db_session.commit()
    return 'Всё ок'


@router.put('/all')
async def update_category() -> str:
    pass


@router.delete('/all')
async def delete_category() -> str:
    pass
