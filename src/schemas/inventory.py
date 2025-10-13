import uuid
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class LotDetailCreate(BaseModel):
    """Schema para registrar ingreso de productos al inventario"""
    presentation_id: uuid.UUID  # ID de la presentación del producto
    quantity_received: int  # Cantidad recibida en bultos/unidades
    unit_cost: float  # Costo unitario de cada bulto/unidad
    batch_number: Optional[str] = None  # Número de lote del proveedor


class LotDetailUpdate(BaseModel):
    """Schema para actualizar detalles de lote"""
    quantity_available: Optional[int] = None
    unit_cost: Optional[float] = None
    batch_number: Optional[str] = None


class LotDetailResponse(BaseModel):
    """Schema para respuesta de detalles de lote"""
    id: uuid.UUID
    lot_id: uuid.UUID
    presentation_id: uuid.UUID
    quantity_received: int
    quantity_available: int
    unit_cost: float
    batch_number: Optional[str] = None

    class Config:
        from_attributes = True


class LotDetailExtendedResponse(BaseModel):
    """
    Schema extendido para respuesta de detalles de lote.
    Incluye información del lote, producto y presentación.
    """
    # Información del LotDetail
    id: uuid.UUID
    lot_id: uuid.UUID
    presentation_id: uuid.UUID
    quantity_received: int
    quantity_available: int
    unit_cost: float
    batch_number: Optional[str] = None
    
    # Información del Lote
    lot_code: str
    received_date: datetime
    expiry_date: Optional[datetime] = None
    lot_status: str
    
    # Información del Producto y Presentación
    product_id: uuid.UUID
    product_name: str
    presentation_name: str
    presentation_unit: str
    
    class Config:
        from_attributes = True


class LotCreate(BaseModel):
    """Schema para crear un nuevo lote de compra"""
    lot_code: str
    supplier_id: uuid.UUID
    received_date: datetime
    expiry_date: Optional[datetime] = None
    status: str = "received"  # valores: received, pending, completed
    total_cost: float
    notes: Optional[str] = None


class LotResponse(BaseModel):
    """Schema para respuesta de lote"""
    id: uuid.UUID
    lot_code: str
    supplier_id: uuid.UUID
    received_date: datetime
    expiry_date: Optional[datetime] = None
    status: str
    total_cost: float
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema para Supplier
class SupplierCreate(BaseModel):
    """Schema para crear un proveedor"""
    name: str
    address: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    contact_person: Optional[str] = None


class SupplierResponse(BaseModel):
    """Schema para respuesta de proveedor"""
    id: uuid.UUID
    name: str
    address: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    contact_person: Optional[str] = None

    class Config:
        from_attributes = True