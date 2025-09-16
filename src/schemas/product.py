import uuid
from typing import Optional

from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    description: str
    category_id: Optional[uuid.UUID] = None
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    image_url: Optional[str] = None


class ProductResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    category_id: Optional[uuid.UUID] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True
