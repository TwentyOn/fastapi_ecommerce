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


@router.post('/token')
async def login(db_session: Annotated[AsyncSession, Depends(get_db)],
                form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(db_session, form_data.username, form_data.password)
    token = await create_access_token(user.id, user.username, user.is_admin, user.is_customer, user.is_supplier,
                                      expires_delta=timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}


async def authenticate_user(db_session: Annotated[AsyncSession, Depends(get_db)], user_name: str, password: str):
    user = await db_session.scalar(select(User).where(User.username == user_name, User.is_active == True))
    if not user or not bcrypt_context.verify(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверные учетные данные',
                            headers={'WWW_Authenticate': 'Bearer'}
                            )
    return user


async def create_access_token(user_id: int, username: str, is_admin: bool, is_customer: bool, is_supplier: bool,
                              expires_delta: timedelta):
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


async def get_current_user(token: Annotated[str, Depends(qauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload['sub']
        user_id: int | None = payload['id']
        is_admin: bool | None = payload['is_admin']
        is_supplier: bool | None = payload['is_supplier']
        is_customer: bool | None = payload['is_customer']
        expire: int | None = payload['exp']

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не удалось подтвердить пользователя')
        if not expire:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Некорректный токен')
        if not isinstance(expire, int):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Некорректный формат токена')
        current_time = datetime.now(timezone.utc).timestamp()
        if expire < current_time:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен истек!')

        return {'user_name': username,
                'user_id': user_id,
                'is_admin': is_admin,
                'is_supplier': is_supplier,
                'is_customer': is_customer}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен истек!')
    except jwt.exceptions:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не удалось подтвердить пользователя')


@router.get('/read_current_user')
async def read_current_user(user: Annotated[dict, Depends(get_current_user)]):
    return {'User': user}
