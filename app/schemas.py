from pydantic import BaseModel, Field


class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category: int


class CreateCategory(BaseModel):
    name: str
    parent_id: int | None = Field(default=None, description='Вместо 0 должно быть null')


class CreateUser(BaseModel):
    name: str
    lastname: str
    username: str
    email: str
    password: str
