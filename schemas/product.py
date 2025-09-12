from pydantic import BaseModel
from typing import Optional
import uuid

class ProductCreate(BaseModel):
    name: str
    description: str
    category_id: Optional[uuid.UUID] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[uuid.UUID] = None

class ProductResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    category_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True