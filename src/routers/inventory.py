"""
Router para manejo de inventario (ingreso de productos) - Versión simplificada
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from utils.auth import get_current_user

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    responses={404: {"description": "Not found"}},
)


@router.get("/test")
async def test_inventory():
    """
    Endpoint de prueba para inventario
    """
    return {"message": "Inventory router funcionando"}


@router.post("/lots/")
async def create_lot(
    lot: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Crear un nuevo lote de compra - Versión simplificada
    """
    try:
        # Simulación básica
        return {
            "message": "Lote creado exitosamente",
            "lot_id": "test-lot-001",
            "supplier_name": lot.get("supplier_name", "Test Supplier"),
            "created_by": current_user.get("id", "unknown")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creando lote: {str(e)}"
        )


@router.get("/lots/")
async def get_lots(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener lista de lotes - Versión simplificada
    """
    return [
        {
            "id": "lot-001",
            "supplier_name": "Proveedor Test 1",
            "purchase_date": "2024-01-15T10:30:00",
            "total_cost": 1500.00
        },
        {
            "id": "lot-002", 
            "supplier_name": "Proveedor Test 2",
            "purchase_date": "2024-01-20T14:30:00",
            "total_cost": 2500.00
        }
    ]


@router.get("/reports/stock")
async def get_stock_report(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generar reporte de stock - Versión simplificada
    """
    return {
        "report": [
            {
                "presentation_id": 1,
                "presentation_name": "Comida Perros 20kg",
                "stock_available": 50,
                "last_updated": datetime.now().isoformat()
            },
            {
                "presentation_id": 2,
                "presentation_name": "Comida Gatos 10kg", 
                "stock_available": 30,
                "last_updated": datetime.now().isoformat()
            }
        ],
        "generated_at": datetime.now().isoformat()
    }