"""
Esquemas para el sistema de ventas
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# Esquemas para SaleDetail
class SaleDetailBase(BaseModel):
    presentation_id: int = Field(..., description="ID de la presentación del producto")
    quantity: int = Field(..., gt=0, description="Cantidad vendida")
    unit_price: float = Field(..., gt=0, description="Precio unitario")
    discount: Optional[float] = Field(0.0, ge=0, description="Descuento aplicado")


class SaleDetailCreate(SaleDetailBase):
    pass


class SaleDetailUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)
    unit_price: Optional[float] = Field(None, gt=0)
    discount: Optional[float] = Field(None, ge=0)


class SaleDetailResponse(SaleDetailBase):
    id: int
    sale_id: int
    subtotal: float = Field(..., description="Subtotal (cantidad * precio - descuento)")
    
    class Config:
        from_attributes = True


# Esquemas para Sale
class SaleBase(BaseModel):
    customer_id: int = Field(..., description="ID del cliente")
    notes: Optional[str] = Field(None, description="Notas adicionales de la venta")


class SaleCreate(SaleBase):
    items: List[SaleDetailCreate] = Field(..., min_items=1, description="Productos vendidos")


class SaleUpdate(BaseModel):
    customer_id: Optional[int] = None
    notes: Optional[str] = None


class SaleResponse(SaleBase):
    id: int
    sale_code: str = Field(..., description="Código único de la venta")
    sale_date: datetime = Field(..., description="Fecha y hora de la venta")
    user_id: int = Field(..., description="ID del usuario que realizó la venta")
    total: float = Field(..., description="Total de la venta")
    items: List[SaleDetailResponse] = Field(default=[], description="Detalles de la venta")
    
    class Config:
        from_attributes = True


# Esquema para crear venta completa
class CompleteSaleCreate(BaseModel):
    """
    Esquema para crear una venta completa con todos sus detalles
    """
    customer_id: int = Field(..., description="ID del cliente")
    notes: Optional[str] = Field(None, description="Notas adicionales")
    items: List[SaleDetailCreate] = Field(..., min_items=1, description="Items de la venta")


# Esquemas para reportes
class SalesReportFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    customer_id: Optional[int] = None
    user_id: Optional[int] = None


class SalesReportItem(BaseModel):
    sale_id: int
    sale_code: str
    sale_date: datetime
    customer_id: int
    user_id: int
    total: float
    items_count: int


class SalesReportResponse(BaseModel):
    sales: List[SalesReportItem]
    total_sales: int
    total_revenue: float
    period_start: Optional[datetime]
    period_end: Optional[datetime]