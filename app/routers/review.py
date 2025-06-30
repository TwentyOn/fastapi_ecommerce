from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert

from typing import Annotated
from datetime import date

from app.backend.db_depends import get_db
from app.models.review import Review
from app.models.products import Product
from app.routers.auth import get_current_user
from app.schemas import CreateReview

router = APIRouter(prefix='/reviews', tags=['отзывы товаров'])


@router.get('/')
async def all_reviews(db_session: Annotated[AsyncSession, Depends(get_db)]):
    all_reviews = await db_session.scalars(select(Review).where(Review.is_active == True))
    return all_reviews.all()


@router.get('/{product_slug}')
async def product_reviews(db_session: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db_session.scalar(select(Product).where(Product.slug == product_slug, Product.is_active == True))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Товара не существует')
    reviews_by_product = await db_session.scalars(select(Review).where(Review.product_id == product.id))
    return reviews_by_product.all()


@router.post('/add')
async def add_review(db_session: Annotated[AsyncSession, Depends(get_db)], product_slug: str, review: CreateReview,
                     get_user: Annotated[dict, Depends(get_current_user)]):
    if not get_user.get('is_customer'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Вы не можетете оставить отзыв данному товару')
    product = await db_session.scalar(select(Product).where(Product.slug == product_slug, Product.is_active == True))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Такого товара не существует')

    await db_session.execute(insert(Review).values(user_id=get_user.get('user_id'),
                                                   product_id=product.id,
                                                   comment=review.comment,
                                                   comment_date=date.today(),
                                                   grade=review.grade))
    await db_session.commit()

    reviews = await db_session.scalars(
        select(Review).where(Review.product_id == product.id))  # получаем все отзывы по заданному товару
    reviews = reviews.all()
    product.rating = sum([rev.grade for rev in reviews]) / len(reviews)  # считаем средний рейтинг
    await db_session.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Отзыв успешно добавлен'}


@router.delete('/delete/{review_id}')
async def delete_review(db_session: Annotated[AsyncSession, Depends(get_db)],
                        get_user: Annotated[dict, Depends(get_current_user)], review_id: int):
    if not get_user.get('is_admin'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')
    review = await db_session.scalar(select(Review).where(Review.id == review_id))
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Отзыв не найден')
    review.is_active = False
    await db_session.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'Отзыв успешно удалён'}
