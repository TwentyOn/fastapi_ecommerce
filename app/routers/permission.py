from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from typing import Annotated

from app.backend.db_depends import get_db
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix='/permission', tags=['permission'])


@router.patch('/')
async def supplier_permission(db_session: Annotated[AsyncSession, Depends(get_db)],
                              get_user: Annotated[dict, Depends(get_current_user)], user_id: int):
    if get_user.get('is_admin'):
        user = await db_session.scalar(select(User).where(User.id == user_id, User.is_active == True))

        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')
        if user.is_supplier:
            user.is_supplier = False
            user.is_customer = True
            await db_session.commit()
            return {'status_code': status.HTTP_200_OK, 'message': 'Пользователь теперь считается покупателем'}
        else:
            user.is_supplier = True
            user.is_customer = False
            await db_session.commit()
            return {'status_code': status.HTTP_200_OK, 'message': 'Пользователь теперь считается поставщиком'}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Вы не имеете прав администратора')
