from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
import jwt

from typing import Annotated
from datetime import datetime, timedelta, timezone

from app.schemas import CreateUser
from app.backend.db_depends import get_db
from app.models.user import User

router = APIRouter(prefix='/auth', tags=['Аутентификация'])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
qauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')

SECRET_KEY = '099d762b52b2b3ce3b81627761f6b705bdf181feb275beccf3602668f96502ec'
ALGORITHM = 'HS256'


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db_session: Annotated[AsyncSession, Depends(get_db)], create_user: CreateUser) -> dict:
    await db_session.execute(insert(User).values(name=create_user.name,
                                                 lastname=create_user.lastname,
                                                 username=create_user.username,
                                                 email=create_user.email,
                                                 password=bcrypt_context.hash(create_user.password)))
    await db_session.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Успех'}


async def authenticate_user(db_session: Annotated[AsyncSession, Depends(get_db)], user_name: str, password: str):
    user = await db_session.scalar(select(User).where(User.username == user_name, User.is_active == True))
    if not user or not bcrypt_context.verify(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверные учетные данные',
                            headers={'WWW_Authenticate': 'Bearer'}
                            )
    return user

async def create_access_token(user_id: int, username: str, is_admin: bool, is_customer: bool, is_supplier: bool, expires_delta: timedelta):
    payload = {
        'sub': username,
        'id': user_id,
        'is_admin': is_admin,
        'is_supplier': is_supplier,
        'is_customer': is_customer,
        'exp': datetime.now(timezone.utc) + expires_delta
    }
    payload['exp'] = int(payload['exp'].timestamp())
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post('/token')
async def login(db_session: Annotated[AsyncSession, Depends(get_db)],
                form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(db_session, form_data.username, form_data.password)
    token = await create_access_token(user.id, user.username, user.is_admin, user.is_customer, user.is_supplier, expires_delta=timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}

@router.get('/read_current_user')
async def read_current_user(user: str = Depends(qauth2_scheme)):
    return user
