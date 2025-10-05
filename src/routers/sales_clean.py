"""
Router para manejo de ventas - Versión simplificada
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from utils.auth import get_current_user

router = APIRouter(
    prefix="/sales",
    tags=["sales"],
    responses={404: {"description": "Not found"}},
)


@router.get("/test")
async def test_sales():
    """
    Endpoint de prueba para ventas
    """
    return {"message": "Sales router funcionando"}


@router.post("/")
async def create_sale(
    sale: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Crear una nueva venta - Versión simplificada
    """
    try:
        # Simulación básica
        return {
            "message": "Venta creada exitosamente",
            "sale_id": "VEN-20241005001",
            "sale_code": "VEN-20241005001",
            "customer_id": sale.get("customer_id", 1),
            "total": sale.get("total", 100.00),
            "created_by": current_user.get("id", "unknown"),
            "sale_date": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creando venta: {str(e)}"
        )


@router.get("/")
async def get_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener lista de ventas - Versión simplificada
    """
    return [
        {
            "id": 1,
            "sale_code": "VEN-20241005001",
            "sale_date": "2024-10-05T10:30:00",
            "customer_id": 1,
            "total": 150.00,
            "user_id": 1
        },
        {
            "id": 2,
            "sale_code": "VEN-20241005002", 
            "sale_date": "2024-10-05T14:30:00",
            "customer_id": 2,
            "total": 225.00,
            "user_id": 1
        }
    ]


@router.get("/reports/summary")
async def get_sales_report(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generar reporte de ventas - Versión simplificada
    """
    return {
        "total_sales": 2,
        "total_revenue": 375.00,
        "period_start": "2024-10-01T00:00:00",
        "period_end": "2024-10-05T23:59:59",
        "generated_at": datetime.now().isoformat()
    }


@router.get("/reports/best-products")
async def get_best_selling_products(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener productos más vendidos - Versión simplificada
    """
    return {
        "best_selling_products": [
            {
                "presentation_id": 1,
                "presentation_name": "Comida Perros Premium 20kg",
                "total_sold": 25,
                "total_revenue": 1250.00
            },
            {
                "presentation_id": 2,
                "presentation_name": "Comida Gatos Premium 10kg",
                "total_sold": 15,
                "total_revenue": 750.00
            }
        ]
    }