from pydantic import BaseModel, ConfigDict

class ProductCreate(BaseModel):
    name: str
    price: float

class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None

class Product(BaseModel):
    id: int
    name: str
    price: float

    model_config = ConfigDict(from_attributes=True)