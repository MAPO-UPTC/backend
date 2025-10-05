
import uuid
from typing import List, Optional
from pydantic import BaseModel


class ProductPresentationCreate(BaseModel):
    presentation_name: str
    quantity: float
    unit: str
    price: float
    sku: Optional[str] = None
    active: Optional[bool] = True

class ProductCreate(BaseModel):
    name: str
    description: str
    brand: Optional[str] = None
    base_unit: Optional[str] = "kg"  # Unidad base por defecto
    category_id: Optional[uuid.UUID] = None
    image_url: Optional[str] = None
    presentations: List[ProductPresentationCreate]

# Esquema para apertura de bulto y habilitar venta a granel
class BulkConversionCreate(BaseModel):
    source_lot_detail_id: int
    target_presentation_id: int  # id de la presentación "granel"
    quantity: float


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    base_unit: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    image_url: Optional[str] = None


class ProductResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    brand: Optional[str] = None
    base_unit: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True
