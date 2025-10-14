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
    source_lot_detail_id: uuid.UUID  # ID del lot_detail del bulto empaquetado
    target_presentation_id: uuid.UUID  # ID de la presentación "granel"
    converted_quantity: int  # Cantidad de bultos a abrir (ej: 1)
    unit_conversion_factor: int  # Cantidad que contiene cada bulto (ej: 25kg)


class BulkConversionResponse(BaseModel):
    id: uuid.UUID
    source_lot_detail_id: uuid.UUID
    target_presentation_id: uuid.UUID
    converted_quantity: int  # Cambiar a int para coincidir con DB
    remaining_bulk: int  # Cambiar a int para coincidir con DB
    conversion_date: str
    status: str

    class Config:
        from_attributes = True


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
