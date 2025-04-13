from fastapi import FastAPI
from app.routers import category

app = FastAPI()

@app.get('/')
async def welcome() -> dict:
    return {'message': 'Welcome!'}

app.include_router(category.router)