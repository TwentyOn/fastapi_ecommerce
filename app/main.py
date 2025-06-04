from fastapi import FastAPI
from app.routers import category, product

app = FastAPI()


@app.get('/')
async def hello() -> dict:
    return {'message': 'Hello!'}


app.include_router(category.router)
app.include_router(product.router)
