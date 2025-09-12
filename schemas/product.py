from pydantic import BaseModel
from typing import Optional
import uuid
from decimal import Decimal

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    stock: int
    category: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Producto Ejemplo",
                "description": "Descripción del producto",
                "price": 29.99,
                "stock": 100,
                "category": "Electrónicos"
            }
        }

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    category: Optional[str] = None

class ProductResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    price: Decimal
    stock: int
    category: Optional[str] = None

    class Config:
        from_attributes = True