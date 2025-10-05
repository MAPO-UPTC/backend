"""
Router para manejo de inventario simplificado
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.inventory import (
    LotCreate, LotResponse, LotDetailCreate, LotDetailResponse
)
from services import inventory_service
from utils.auth import get_current_user
from schemas.user import UserResponse

router = APIRouter()


@router.post("/lots/", response_model=dict)
async def create_lot(
    lot: LotCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Crear un nuevo lote de compra
    """
    try:
        db_lot = inventory_service.create_lot(db, lot)
        return db_lot
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creando lote: {str(e)}"
        )


@router.post("/lots/{lot_id}/details/", response_model=LotDetailResponse)
async def create_lot_detail(
    lot_id: str,
    lot_detail: LotDetailCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("inventory_write"))
):
    """
    Agregar un detalle (producto) a un lote existente
    """
    try:
        # Verificar que el lote existe
        lot = inventory_service.get_lot_by_id(db, lot_id)
        if not lot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lote con ID {lot_id} no encontrado"
            )
        
        db_lot_detail = inventory_service.create_lot_detail(db, lot_detail, lot_id)
        return db_lot_detail
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando detalle de lote: {str(e)}"
        )


@router.post("/lots/complete/", response_model=dict)
async def create_complete_lot(
    lot_data: dict,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Crear un lote completo con sus detalles en una sola operación
    
    Estructura esperada:
    {
        "lot": {
            "supplier_name": "Proveedor XYZ",
            "purchase_date": "2024-01-15T10:30:00",
            "invoice_number": "FAC-001",
            "total_cost": 1500.00,
            "notes": "Compra mensual"
        },
        "details": [
            {
                "presentation_id": 1,
                "quantity_received": 50,
                "unit_cost": 15.00,
                "batch_number": "LOTE001",
                "expiry_date": "2025-12-31T00:00:00",
                "supplier_info": "Importado directo"
            }
        ]
    }
    """
    try:
        lot_info = LotCreate(**lot_data.get("lot", {}))
        details_info = [LotDetailCreate(**detail) for detail in lot_data.get("details", [])]
        
        if not details_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe incluir al menos un detalle en el lote"
            )
        
        db_lot = inventory_service.create_lot_with_details(db, lot_info, details_info)
        return db_lot
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creando lote completo: {str(e)}"
        )


@router.get("/lots/", response_model=List[dict])
async def get_lots(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Obtener lista de lotes con paginación
    """
    lots = inventory_service.get_lots(db, skip=skip, limit=limit)
    return lots


@router.get("/lots/{lot_id}", response_model=LotResponse)
async def get_lot(
    lot_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("inventory_read"))
):
    """
    Obtener un lote específico por su ID
    """
    lot = inventory_service.get_lot_by_id(db, lot_id)
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lote con ID {lot_id} no encontrado"
        )
    return lot


@router.get("/lots/{lot_id}/details/", response_model=List[LotDetailResponse])
async def get_lot_details(
    lot_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("inventory_read"))
):
    """
    Obtener todos los detalles de un lote específico
    """
    # Verificar que el lote existe
    lot = inventory_service.get_lot_by_id(db, lot_id)
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lote con ID {lot_id} no encontrado"
        )
    
    details = inventory_service.get_lot_details_by_lot(db, lot_id)
    return details


@router.get("/stock/presentation/{presentation_id}")
async def get_stock_by_presentation(
    presentation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("inventory_read"))
):
    """
    Obtener el stock disponible para una presentación específica
    """
    stock = inventory_service.get_available_stock_by_presentation(db, presentation_id)
    return {"presentation_id": presentation_id, "available_stock": stock}


@router.get("/reports/stock")
async def get_stock_report(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("inventory_read"))
):
    """
    Generar reporte de stock actual
    """
    report = inventory_service.get_stock_report(db)
    return {"report": report, "generated_at": datetime.now().isoformat()}


@router.post("/stock/reduce/{presentation_id}")
async def reduce_stock(
    presentation_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("inventory_write"))
):
    """
    Reducir stock de una presentación (para ventas)
    """
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cantidad debe ser mayor a 0"
        )
    
    success = inventory_service.reduce_stock(db, presentation_id, quantity)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock insuficiente para la cantidad solicitada"
        )
    
    return {
        "message": f"Stock reducido exitosamente: {quantity} unidades",
        "presentation_id": presentation_id,
        "quantity_reduced": quantity
    }