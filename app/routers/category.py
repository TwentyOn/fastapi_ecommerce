from fastapi import APIRouter

router = APIRouter(prefix='/categories', tags=['категории'])


@router.get('/all')
async def get_all_categories() -> str:
    return 'пока нет категорий'


@router.post('/all')
async def create_category() -> str:
    pass


@router.put('/all')
async def update_category() -> str:
    pass


@router.delete('/all')
async def delete_category() -> str:
    pass
