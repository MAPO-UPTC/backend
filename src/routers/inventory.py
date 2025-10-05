"""
Router para manejo de inventario (ingreso de productos)
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from utils.auth import get_current_user
from schemas.inventory import LotCreate, LotResponse, LotDetailCreate, LotDetailResponse, SupplierCreate, SupplierResponse
from services.inventory_service import (
    create_lot,
    create_lot_with_details,
    get_lots,
    get_lot_by_id,
    get_lot_details_by_lot,
    get_stock_report,
    get_available_stock_by_presentation,
    create_supplier,
    get_suppliers,
    get_supplier_by_id
)

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


@router.post("/lots/", response_model=LotResponse)
async def create_lot_endpoint(
    lot: LotCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Crear un nuevo lote de compra
    """
    try:
        db_lot = create_lot(db, lot)
        return db_lot
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creando lote: {str(e)}"
        )


@router.get("/lots/", response_model=List[LotResponse])
async def get_lots_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener lista de lotes con paginación
    """
    try:
        lots = get_lots(db, skip=skip, limit=limit)
        return lots
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo lotes: {str(e)}"
        )


@router.get("/reports/stock")
async def get_stock_report_endpoint(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generar reporte de stock actual
    """
    try:
        report = get_stock_report(db)
        return {
            "report": report,
            "generated_at": datetime.now().isoformat(),
            "generated_by": current_user.get("id", "unknown")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando reporte: {str(e)}"
        )


@router.post("/lots/{lot_id}/details/", response_model=LotDetailResponse)
async def add_product_to_lot(
    lot_id: str,
    lot_detail: LotDetailCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Agregar un producto específico a un lote existente
    """
    try:
        # Verificar que el lote existe
        lot = get_lot_by_id(db, lot_id)
        if not lot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lote con ID {lot_id} no encontrado"
            )
        
        from services.inventory_service import create_lot_detail
        db_lot_detail = create_lot_detail(db, lot_detail, lot_id)
        return db_lot_detail
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error agregando producto al lote: {str(e)}"
        )


@router.get("/lots/{lot_id}/details/", response_model=List[LotDetailResponse])
async def get_lot_details(
    lot_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener todos los productos en un lote específico
    """
    try:
        details = get_lot_details_by_lot(db, lot_id)
        return details
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo detalles del lote: {str(e)}"
        )


@router.get("/stock/{presentation_id}")
async def get_stock_by_presentation(
    presentation_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener stock disponible para una presentación específica
    """
    try:
        stock = get_available_stock_by_presentation(db, presentation_id)
        return {
            "presentation_id": presentation_id,
            "available_stock": stock,
            "checked_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo stock: {str(e)}"
        )


# ENDPOINTS PARA PROVEEDORES
# ==========================

@router.post("/suppliers/", response_model=SupplierResponse)
async def create_supplier_endpoint(
    supplier: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Crear un nuevo proveedor
    """
    try:
        db_supplier = create_supplier(db, supplier)
        return db_supplier
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando proveedor: {str(e)}"
        )


@router.get("/suppliers/", response_model=List[SupplierResponse])
async def get_suppliers_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener lista de proveedores
    """
    try:
        suppliers = get_suppliers(db, skip=skip, limit=limit)
        return suppliers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo proveedores: {str(e)}"
        )


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier_by_id_endpoint(
    supplier_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener un proveedor específico por ID
    """
    try:
        supplier = get_supplier_by_id(db, supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proveedor con ID {supplier_id} no encontrado"
            )
        return supplier
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo proveedor: {str(e)}"
        )