"""
Router para manejo de ventas - Versión simplificada
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from utils.auth import get_current_user_from_db
from schemas.sales import SimpleSaleCreate, SaleResponse, SalesReportFilter, SaleDetailFullResponse
from services.sales_service import (
    create_sale,
    get_sales,
    get_sale_by_id,
    get_sale_by_code,
    get_sale_details_by_sale,
    get_sales_report,
    get_best_selling_products,
    get_daily_sales_summary,
    get_sale_full_details
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
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Cantidad máxima de resultados"),
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio (opcional) - formato ISO 8601"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin (opcional) - formato ISO 8601"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_db)
):
    """
    Obtener lista de ventas con paginación y filtros opcionales.
    
    - **skip**: Número de registros a saltar para paginación (default: 0)
    - **limit**: Cantidad máxima de resultados (default: 100, max: 1000)
    - **start_date**: Filtrar ventas desde esta fecha (opcional, formato: 2025-10-01T00:00:00)
    - **end_date**: Filtrar ventas hasta esta fecha (opcional, formato: 2025-10-31T23:59:59)
    
    Las ventas se devuelven ordenadas de más reciente a más antigua.
    
    Ejemplos:
    - Todas las ventas: `/sales/`
    - Ventas de octubre 2025: `/sales/?start_date=2025-10-01T00:00:00&end_date=2025-10-31T23:59:59`
    - Últimas 50 ventas: `/sales/?limit=50`
    - Página 2 (50 siguientes): `/sales/?skip=50&limit=50`
    """
    try:
        sales = get_sales(
            db, 
            skip=skip, 
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
        return sales
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo ventas: {str(e)}"
        )


@router.get("/{sale_id}/details", response_model=SaleDetailFullResponse)
async def get_sale_full_details_endpoint(
    sale_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_from_db)
):
    """
    Obtener detalles completos de una venta específica.
    
    Incluye:
    - Información completa de la venta
    - Información del cliente (nombre, documento)
    - Información del vendedor
    - Detalles de cada item con:
      - Nombre del producto
      - Nombre de la presentación
      - Precio de costo
      - Cantidad y precio de venta
      - Total por línea
    
    Parámetros:
    - **sale_id**: UUID de la venta
    
    Ejemplo de respuesta:
    ```json
    {
      "id": "uuid-venta",
      "sale_code": "VEN-20251012120000",
      "sale_date": "2025-10-12T12:00:00",
      "customer_name": "Juan Pérez",
      "customer_document": "CC: 1234567890",
      "seller_name": "María García",
      "total": 45.50,
      "status": "completed",
      "items": [
        {
          "product_name": "Arroz Diana",
          "presentation_name": "Paquete x 500g",
          "quantity": 2,
          "unit_price": 12.50,
          "cost_price": 8.00,
          "line_total": 25.00
        }
      ]
    }
    ```
    """
    try:
        sale_details = get_sale_full_details(db, sale_id)
        
        if not sale_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Venta con ID {sale_id} no encontrada"
            )
        
        return sale_details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo detalles de venta: {str(e)}"
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