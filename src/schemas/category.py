from uuid import UUID
from pydantic import BaseModel
from typing import Optional


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


# Crear categoría
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


#  Actualizar categoría
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Producto resumido (cuando se devuelve dentro de una categoría)
class ProductOut(BaseModel):
    id: UUID
    name: str
    price: float
    stock: int

    class Config:
        orm_mode = True

# Para devolver categoría (ejemplo de CategoryOut)
class CategoryOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True
