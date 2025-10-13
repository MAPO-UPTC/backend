"""
Router para manejo de inventario (ingreso de productos)
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from utils.auth import get_current_user
from schemas.inventory import LotCreate, LotResponse, LotDetailCreate, LotDetailResponse, SupplierCreate, SupplierResponse, LotDetailExtendedResponse
from models_db import Lot, ProductPresentation, Product
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
    get_supplier_by_id,
    get_lot_details_by_presentation
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


@router.get("/presentations/{presentation_id}/lot-details")
async def get_presentation_lot_details(
    presentation_id: str,
    available_only: bool = Query(True, description="Filtrar solo lotes con stock disponible"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener detalles de todos los lotes disponibles para una presentación específica.
    Ordenados por FIFO (First In, First Out) - más antiguo primero.
    
    Este endpoint es esencial para:
    - Conversión de empaquetado a granel (obtener lote más antiguo)
    - Visualizar distribución de stock por lotes
    - Implementar lógica FIFO en el frontend
    
    Args:
        presentation_id: UUID de la presentación
        available_only: Si True, solo retorna lotes con quantity_available > 0
    
    Returns:
        Lista de LotDetail con información extendida (producto, lote, etc.)
    """
    try:
        # Validar UUID
        import uuid as uuid_lib
        try:
            uuid_lib.UUID(presentation_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El ID de presentación '{presentation_id}' no es un UUID válido"
            )
        
        # Obtener lot_details usando la función del servicio
        lot_details = get_lot_details_by_presentation(
            db, 
            presentation_id,
            available_only=available_only
        )
        
        # Si no hay lotes disponibles
        if not lot_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No hay lotes disponibles para la presentación {presentation_id}"
            )
        
        # Construir respuesta extendida con información del producto y lote
        result = []
        for detail in lot_details:
            # Obtener lote
            lot = db.query(Lot).filter(Lot.id == detail.lot_id).first()
            
            # Obtener presentación y producto
            presentation = db.query(ProductPresentation).filter(
                ProductPresentation.id == detail.presentation_id
            ).first()
            
            product = None
            if presentation:
                product = db.query(Product).filter(
                    Product.id == presentation.product_id
                ).first()
            
            # Construir objeto de respuesta
            result.append({
                # Información del LotDetail
                "id": str(detail.id),
                "lot_id": str(detail.lot_id),
                "presentation_id": str(detail.presentation_id),
                "quantity_received": detail.quantity_received,
                "quantity_available": detail.quantity_available,
                "unit_cost": float(detail.unit_cost),
                "batch_number": detail.batch_number,
                
                # Información del Lote
                "lot_code": lot.lot_code if lot else None,
                "received_date": lot.received_date.isoformat() if lot and lot.received_date else None,
                "expiry_date": lot.expiry_date.isoformat() if lot and lot.expiry_date else None,
                "lot_status": lot.status if lot else None,
                
                # Información del Producto y Presentación
                "product_id": str(product.id) if product else None,
                "product_name": product.name if product else None,
                "presentation_name": presentation.presentation_name if presentation else None,
                "presentation_unit": presentation.unit if presentation else None,
            })
        
        # Calcular metadata
        total_available = sum(detail.quantity_available for detail in lot_details)
        oldest_date = min(lot.received_date for lot in [
            db.query(Lot).filter(Lot.id == d.lot_id).first() for d in lot_details
        ] if lot) if lot_details else None
        newest_date = max(lot.received_date for lot in [
            db.query(Lot).filter(Lot.id == d.lot_id).first() for d in lot_details
        ] if lot) if lot_details else None
        
        return {
            "success": True,
            "data": result,
            "count": len(result),
            "metadata": {
                "presentation_id": presentation_id,
                "total_available_quantity": total_available,
                "oldest_lot_date": oldest_date.isoformat() if oldest_date else None,
                "newest_lot_date": newest_date.isoformat() if newest_date else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo detalles de lotes: {str(e)}"
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