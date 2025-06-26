from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from typing import Annotated

from app.schemas import CreateUser
from app.backend.db_depends import get_db
from app.models.user import User

router = APIRouter(prefix='/auth', tags=['Аутентификация'])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.post('/', status_code=status.HTTP_201_CREATED)
async def get_all_users(db_session: Annotated[AsyncSession, Depends(get_db)], create_user: CreateUser) -> dict:
    await db_session.execute(insert(User).values(name=create_user.name,
                                                 lastname=create_user.lastname,
                                                 username=create_user.username,
                                                 email=create_user.email,
                                                 password=bcrypt_context.hash(create_user.password)))
    await db_session.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Успех'}
