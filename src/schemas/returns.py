"""
Schemas para manejo de devoluciones
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ReturnDetailCreate(BaseModel):
    """Schema para crear un detalle de devolución"""

    sale_detail_id: uuid.UUID = Field(
        ..., description="ID del detalle de venta original"
    )
    quantity_returned: int = Field(..., gt=0, description="Cantidad a devolver")
    condition: str = Field(
        ..., description="Condición del producto: good, damaged, expired"
    )

    @field_validator("condition")
    @classmethod
    def validate_condition(cls, v):
        valid_conditions = ["good", "damaged", "expired"]
        if v not in valid_conditions:
            raise ValueError(
                f"Condición inválida. Debe ser: {', '.join(valid_conditions)}"
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "sale_detail_id": "550e8400-e29b-41d4-a716-446655440000",
                "quantity_returned": 2,
                "condition": "good",
            }
        }


class ReturnCreate(BaseModel):
    """Schema para crear una devolución"""

    sale_id: uuid.UUID = Field(..., description="ID de la venta original")
    reason: str = Field(..., min_length=5, description="Motivo de la devolución")
    notes: Optional[str] = Field(None, description="Notas adicionales")
    items: List[ReturnDetailCreate] = Field(
        ..., min_length=1, description="Items a devolver"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "sale_id": "550e8400-e29b-41d4-a716-446655440000",
                "reason": "Producto defectuoso",
                "notes": "Cliente reporta que el producto no funciona correctamente",
                "items": [
                    {
                        "sale_detail_id": "660e8400-e29b-41d4-a716-446655440000",
                        "quantity_returned": 1,
                        "condition": "damaged",
                    }
                ],
            }
        }


class ReturnDetailResponse(BaseModel):
    """Schema de respuesta para detalle de devolución"""

    id: uuid.UUID
    return_id: uuid.UUID
    sale_detail_id: uuid.UUID
    presentation_id: uuid.UUID
    quantity_returned: int
    unit_price: float
    refund_amount: float
    condition: str
    restocked: bool
    lot_detail_id: Optional[uuid.UUID] = None
    bulk_conversion_id: Optional[uuid.UUID] = None

    # Campos adicionales para la respuesta
    product_name: Optional[str] = None
    presentation_name: Optional[str] = None

    class Config:
        from_attributes = True


class ReturnResponse(BaseModel):
    """Schema de respuesta para devolución"""

    id: uuid.UUID
    return_code: str
    return_date: datetime
    sale_id: uuid.UUID
    customer_id: uuid.UUID
    processed_by_user_id: uuid.UUID
    reason: str
    total_refund: float
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Información adicional
    customer_name: Optional[str] = None
    processed_by_name: Optional[str] = None
    sale_code: Optional[str] = None

    # Items de la devolución
    items: List[ReturnDetailResponse] = []

    class Config:
        from_attributes = True


class ReturnUpdateStatus(BaseModel):
    """Schema para actualizar el estado de una devolución"""

    status: str = Field(..., description="Nuevo estado de la devolución")
    notes: Optional[str] = Field(None, description="Notas sobre el cambio de estado")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        valid_statuses = ["pending", "approved", "rejected", "completed"]
        if v not in valid_statuses:
            raise ValueError(f"Estado inválido. Debe ser: {', '.join(valid_statuses)}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "status": "approved",
                "notes": "Devolución aprobada por gerencia",
            }
        }


class ReturnProcessRequest(BaseModel):
    """Schema para procesar una devolución y devolver al inventario"""

    return_id: uuid.UUID = Field(..., description="ID de la devolución a procesar")

    class Config:
        json_schema_extra = {
            "example": {"return_id": "550e8400-e29b-41d4-a716-446655440000"}
        }


class ReturnStatsResponse(BaseModel):
    """Schema para estadísticas de devoluciones"""

    total_returns: int
    total_refunded: float
    returns_by_status: dict
    returns_by_condition: dict
    most_returned_products: List[dict]

    class Config:
        json_schema_extra = {
            "example": {
                "total_returns": 45,
                "total_refunded": 15000.50,
                "returns_by_status": {
                    "pending": 5,
                    "approved": 10,
                    "rejected": 2,
                    "completed": 28,
                },
                "returns_by_condition": {"good": 30, "damaged": 10, "expired": 5},
                "most_returned_products": [
                    {
                        "product_name": "Aceite Vegetal",
                        "total_returned": 15,
                        "total_refund": 5000.0,
                    }
                ],
            }
        }
