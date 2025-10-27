"""
Esquemas para reportes de ventas
"""

import uuid
from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ReportPeriod(str, Enum):
    """Periodo del reporte"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TopProductItem(BaseModel):
    """Producto más vendido"""

    presentation_id: uuid.UUID
    product_name: str
    presentation_name: str
    total_quantity: int = Field(..., description="Cantidad total vendida")
    total_revenue: float = Field(..., description="Ingresos totales generados")
    average_price: float = Field(..., description="Precio promedio de venta")

    class Config:
        from_attributes = True


class TopCustomerItem(BaseModel):
    """Mejor cliente"""

    customer_id: uuid.UUID
    customer_name: str
    customer_document: str
    total_purchases: int = Field(..., description="Número total de compras")
    total_spent: float = Field(..., description="Total gastado")
    average_purchase: float = Field(..., description="Valor promedio por compra")

    class Config:
        from_attributes = True


class SalesReportResponse(BaseModel):
    """Respuesta del reporte de ventas"""

    period: ReportPeriod = Field(..., description="Periodo del reporte")
    start_date: datetime = Field(..., description="Fecha de inicio del periodo")
    end_date: datetime = Field(..., description="Fecha de fin del periodo")

    # Métricas generales
    total_sales: int = Field(..., description="Número total de ventas")
    total_revenue: float = Field(..., description="Ingresos totales")
    estimated_profit: float = Field(..., description="Ganancia estimada (ingresos - costos)")
    profit_margin: float = Field(..., description="Margen de ganancia en porcentaje")

    # Top productos y clientes
    top_products: List[TopProductItem] = Field(
        default=[], description="Productos más vendidos"
    )
    top_customers: List[TopCustomerItem] = Field(
        default=[], description="Mejores clientes"
    )

    # Métricas adicionales
    average_sale_value: float = Field(..., description="Valor promedio por venta")
    total_items_sold: int = Field(..., description="Total de items vendidos")

    class Config:
        from_attributes = True


class ReportRequest(BaseModel):
    """Solicitud de reporte"""

    period: ReportPeriod = Field(..., description="Periodo del reporte (daily, weekly, monthly)")
    reference_date: date = Field(
        ..., description="Fecha de referencia para el reporte (formato: YYYY-MM-DD)"
    )
    top_limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Límite de items para top productos y clientes",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "period": "daily",
                "reference_date": "2025-10-21",
                "top_limit": 10
            }
        }
