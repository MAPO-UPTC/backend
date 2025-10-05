import uuid
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class LotDetailCreate(BaseModel):
    """Schema para registrar ingreso de productos al inventario"""
    lot_id: uuid.UUID  # ID del lote de compra/recepción
    presentation_id: int  # ID de la presentación del producto
    quantity_received: int  # Cantidad recibida en bultos/unidades
    unit_cost: float  # Costo unitario de cada bulto/unidad
    batch_number: Optional[str] = None  # Número de lote del proveedor
    expiry_date: Optional[datetime] = None  # Fecha de vencimiento
    supplier_info: Optional[str] = None  # Información del proveedor


class LotDetailUpdate(BaseModel):
    """Schema para actualizar detalles de lote"""
    quantity_available: Optional[int] = None
    unit_cost: Optional[float] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[datetime] = None
    supplier_info: Optional[str] = None


class LotDetailResponse(BaseModel):
    """Schema para respuesta de detalles de lote"""
    id: uuid.UUID
    lot_id: uuid.UUID
    presentation_id: int
    quantity_received: int
    quantity_available: int
    unit_cost: float
    batch_number: Optional[str] = None
    expiry_date: Optional[datetime] = None
    supplier_info: Optional[str] = None

    class Config:
        from_attributes = True


class LotCreate(BaseModel):
    """Schema para crear un nuevo lote de compra"""
    supplier_name: str
    purchase_date: datetime
    invoice_number: Optional[str] = None
    total_cost: float
    notes: Optional[str] = None


class LotResponse(BaseModel):
    """Schema para respuesta de lote"""
    id: uuid.UUID
    supplier_name: str
    purchase_date: datetime
    invoice_number: Optional[str] = None
    total_cost: float
    notes: Optional[str] = None

    class Config:
        from_attributes = True