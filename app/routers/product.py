from fastapi import APIRouter

router = APIRouter(prefix='/products', tags=['продукты'])


@router.get('/')
async def all_products():
    pass


@router.post('/')
async def create_product():
    pass


@router.get('/{category_slug}')
async def get_product_by_category(category_slug: str):
    pass


@router.get('/detail/{product_slug}')
async def detail_product(product_slug: str):
    pass


@router.put('/{product_slug}')
async def update_product(product_slug: str):
    pass


@router.delete('/{product_slug}')
def delete_product(product_slug: str):
    pass
