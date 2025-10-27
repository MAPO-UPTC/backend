"""
Router para reportes de ventas
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.reports import ReportRequest, SalesReportResponse
from services.reports_service import generate_sales_report
from utils.auth import get_current_user_from_db

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    responses={404: {"description": "Not found"}},
)


@router.post("/sales", response_model=SalesReportResponse)
async def get_sales_report(
    report_request: ReportRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_from_db),
):
    """
    Generar reporte de ventas según periodo y fecha
    
    **Periodos disponibles:**
    - `daily`: Reporte del día específico
    - `weekly`: Reporte de la semana (lunes a domingo) que contiene la fecha
    - `monthly`: Reporte del mes completo
    
    **Incluye:**
    - Ventas totales del periodo
    - Ingresos totales
    - Ganancia estimada (ingresos - costos)
    - Margen de ganancia
    - Top productos más vendidos (configurable)
    - Mejores clientes (configurable)
    - Valor promedio por venta
    - Total de items vendidos
    
    **Ejemplo de uso:**
    ```json
    {
        "period": "daily",
        "reference_date": "2025-10-21",
        "top_limit": 10
    }
    ```
    
    **Respuesta incluye:**
    - Fecha de inicio y fin del periodo calculado
    - Métricas generales de ventas
    - Lista de productos más vendidos con cantidades y ingresos
    - Lista de mejores clientes con compras totales y gastos
    """
    try:
        report = generate_sales_report(
            db,
            period=report_request.period,
            reference_date=report_request.reference_date,
            top_limit=report_request.top_limit,
        )
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando reporte: {str(e)}",
        )


@router.get("/sales/quick/{period}")
async def get_quick_sales_report(
    period: str,
    reference_date: date,
    top_limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_from_db),
):
    """
    Generar reporte de ventas rápido usando parámetros de query
    
    **Parámetros:**
    - `period`: Periodo del reporte (daily, weekly, monthly)
    - `reference_date`: Fecha de referencia (formato: YYYY-MM-DD)
    - `top_limit`: Límite de items para tops (default: 10, max: 50)
    
    **Ejemplos:**
    - Reporte diario: `/reports/sales/quick/daily?reference_date=2025-10-21`
    - Reporte semanal: `/reports/sales/quick/weekly?reference_date=2025-10-21&top_limit=5`
    - Reporte mensual: `/reports/sales/quick/monthly?reference_date=2025-10-01`
    """
    try:
        # Validar periodo
        valid_periods = ["daily", "weekly", "monthly"]
        if period not in valid_periods:
            raise ValueError(
                f"Periodo inválido. Debe ser uno de: {', '.join(valid_periods)}"
            )
        
        # Validar top_limit
        if top_limit < 1 or top_limit > 50:
            raise ValueError("top_limit debe estar entre 1 y 50")
        
        report = generate_sales_report(
            db,
            period=period,
            reference_date=reference_date,
            top_limit=top_limit,
        )
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando reporte: {str(e)}",
        )
