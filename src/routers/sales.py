"""
Router para manejo de ventas simplificado
"""
from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.sales import CompleteSaleCreate
from services import sales_service
from utils.auth import get_current_user
from schemas.user import UserResponse

router = APIRouter()


@router.post("/", response_model=dict)
async def create_sale(
    sale: CompleteSaleCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Crear una nueva venta
    """
    try:
        user_id = current_user.id
        db_sale = sales_service.create_sale(db, sale, user_id)
        return {"message": "Venta creada exitosamente", "sale_id": db_sale.id, "sale_code": db_sale.sale_code}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando venta: {str(e)}"
        )


@router.get("/", response_model=List[dict])
async def get_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    customer_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Obtener lista de ventas con filtros opcionales
    """
    if customer_id:
        sales = sales_service.get_sales_by_customer(db, customer_id, skip=skip, limit=limit)
    elif user_id:
        sales = sales_service.get_sales_by_user(db, user_id, skip=skip, limit=limit)
    else:
        sales = sales_service.get_sales(db, skip=skip, limit=limit)
    
    return [{"id": sale.id, "sale_code": sale.sale_code, "total": sale.total, "sale_date": sale.sale_date.isoformat()} for sale in sales]


@router.get("/{sale_id}", response_model=dict)
async def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Obtener una venta específica por su ID
    """
    sale = sales_service.get_sale_by_id(db, sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venta con ID {sale_id} no encontrada"
        )
    return {"id": sale.id, "sale_code": sale.sale_code, "total": sale.total, "sale_date": sale.sale_date.isoformat()}


@router.delete("/{sale_id}")
async def cancel_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Cancelar una venta y restaurar el inventario
    """
    success = sales_service.cancel_sale(db, sale_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venta con ID {sale_id} no encontrada"
        )
    
    return {"message": f"Venta {sale_id} cancelada exitosamente"}