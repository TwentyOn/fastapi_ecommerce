from fastapi import APIRouter

router = APIRouter(prefix='/products', tags='Продукты')

@router.get('/')
async def get_all_products() -> dict:
    pass

@router.post('/')
async def create_product():
    pass

@router.get('/{category_slug}')
async def get_product_by_category(category_slug: str) -> str:
    pass

router.get('/detail/{product_slug}')