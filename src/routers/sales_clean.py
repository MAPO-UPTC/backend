"""
Router para manejo de ventas - Versión simplificada
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from utils.auth import get_current_user_from_db
from schemas.sales import SimpleSaleCreate, SaleResponse, SalesReportFilter
from services.sales_service import (
    create_sale,
    get_sales,
    get_sale_by_id,
    get_sale_by_code,
    get_sale_details_by_sale,
    get_sales_report,
    get_best_selling_products,
    get_daily_sales_summary
)

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


@router.post("/", response_model=SaleResponse)
async def create_sale_endpoint(
    sale: SimpleSaleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_db)
):
    """
    Crear una nueva venta completa con sus detalles
    """
    try:
        # Obtener el ID del usuario desde la base de datos
        user_id = str(current_user.id)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no identificado"
            )
        # Convertir a dict para compatibilidad con el servicio
        sale_data = sale.dict()
        
        db_sale = create_sale(db, sale_data, user_id)
        return db_sale
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


@router.get("/", response_model=List[SaleResponse])
async def get_sales_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_db)
):
    """
    Obtener lista de ventas con paginación
    """
    try:
        sales = get_sales(db, skip=skip, limit=limit)
        return sales
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo ventas: {str(e)}"
        )


@router.get("/reports/summary")
async def get_sales_report_endpoint(
    start_date: datetime = None,
    end_date: datetime = None,
    customer_id: str = None,
    user_id: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_db)
):
    """
    Generar reporte de ventas con filtros opcionales
    """
    try:
        filters = SalesReportFilter(
            start_date=start_date,
            end_date=end_date,
            customer_id=customer_id,
            user_id=user_id
        )
        report = get_sales_report(db, filters)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando reporte: {str(e)}"
        )


@router.get("/reports/best-products")
async def get_best_selling_products_endpoint(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_db)
):
    """
    Obtener productos más vendidos
    """
    try:
        products = get_best_selling_products(db, limit=limit)
        return {
            "best_selling_products": products,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo productos más vendidos: {str(e)}"
        )


@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale_by_id_endpoint(
    sale_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_db)
):
    """
    Obtener una venta específica por ID
    """
    try:
        sale = get_sale_by_id(db, sale_id)
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Venta con ID {sale_id} no encontrada"
            )
        return sale
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo venta: {str(e)}"
        )


@router.get("/code/{sale_code}", response_model=SaleResponse)
async def get_sale_by_code_endpoint(
    sale_code: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_db)
):
    """
    Obtener una venta específica por código
    """
    try:
        sale = get_sale_by_code(db, sale_code)
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Venta con código {sale_code} no encontrada"
            )
        return sale
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo venta: {str(e)}"
        )


@router.get("/reports/daily/{date}")
async def get_daily_summary(
    date: datetime,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_db)
):
    """
    Obtener resumen de ventas para un día específico
    """
    try:
        summary = get_daily_sales_summary(db, date)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo resumen diario: {str(e)}"
        )