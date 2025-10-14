"""
Esquemas para el sistema de ventas - Versión simplificada
"""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# Esquemas simplificados para crear ventas
class SimpleSaleItem(BaseModel):
    """
    Item simplificado para crear una venta
    """

    presentation_id: uuid.UUID = Field(
        ..., description="ID de la presentación del producto"
    )
    quantity: int = Field(..., gt=0, description="Cantidad a vender")
    unit_price: float = Field(..., gt=0, description="Precio unitario")


class SimpleSaleCreate(BaseModel):
    """
    Esquema simplificado para crear una venta
    """

    customer_id: uuid.UUID = Field(..., description="ID del cliente (person)")
    status: str = Field(default="completed", description="Estado de la venta")
    items: List[SimpleSaleItem] = Field(
        ..., min_items=1, description="Items de la venta"
    )


# Esquemas de respuesta
class SaleDetailResponse(BaseModel):
    id: uuid.UUID
    sale_id: uuid.UUID
    presentation_id: uuid.UUID
    lot_detail_id: Optional[uuid.UUID] = None
    bulk_conversion_id: Optional[uuid.UUID] = None
    quantity: int
    unit_price: float
    line_total: float

    class Config:
        from_attributes = True


class SaleDetailExtended(BaseModel):
    """
    Detalle de venta extendido con información del producto
    """

    id: uuid.UUID
    sale_id: uuid.UUID
    presentation_id: uuid.UUID
    lot_detail_id: Optional[uuid.UUID] = None
    bulk_conversion_id: Optional[uuid.UUID] = None
    quantity: int
    unit_price: float
    line_total: float

    # Información del producto
    product_name: str = Field(..., description="Nombre del producto")
    presentation_name: str = Field(..., description="Nombre de la presentación")
    cost_price: float = Field(..., description="Precio de costo del producto")

    class Config:
        from_attributes = True


class SaleResponse(BaseModel):
    id: uuid.UUID
    sale_code: str
    sale_date: datetime
    customer_id: uuid.UUID
    user_id: uuid.UUID
    total: float
    status: str
    items: List[SaleDetailResponse] = Field(default=[])

    class Config:
        from_attributes = True


class SaleDetailFullResponse(BaseModel):
    """
    Respuesta completa de una venta con detalles extendidos de productos
    """

    id: uuid.UUID
    sale_code: str
    sale_date: datetime
    customer_id: uuid.UUID
    user_id: uuid.UUID
    total: float
    status: str

    # Información del cliente
    customer_name: str = Field(..., description="Nombre completo del cliente")
    customer_document: str = Field(..., description="Documento del cliente")

    # Información del vendedor
    seller_name: str = Field(..., description="Nombre del vendedor")

    # Items con información extendida
    items: List[SaleDetailExtended] = Field(
        default=[], description="Detalles de la venta con info de productos"
    )

    class Config:
        from_attributes = True


# Esquemas para reportes
class SalesReportFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    customer_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None


class SalesReportItem(BaseModel):
    sale_id: uuid.UUID
    sale_code: str
    sale_date: datetime
    customer_id: uuid.UUID
    user_id: uuid.UUID
    total: float
    status: str


class SalesReportResponse(BaseModel):
    sales: List[SalesReportItem]
    total_sales: int
    total_revenue: float
    period_start: Optional[datetime]
    period_end: Optional[datetime]


class ProductSalesStats(BaseModel):
    presentation_id: uuid.UUID
    presentation_name: str
    total_sold: int
    total_revenue: float


class DailySalesSummary(BaseModel):
    date: datetime
    total_sales: int
    total_revenue: float
    total_items_sold: int
    average_sale_value: float
