"""
Router para manejo de devoluciones
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from config.permissions import Action, Entity
from database import get_db
from schemas.returns import (
    ReturnCreate,
    ReturnProcessRequest,
    ReturnResponse,
    ReturnStatsResponse,
    ReturnUpdateStatus,
)
from services.returns_service import (
    create_return,
    get_return_by_code,
    get_return_by_id,
    get_return_full_details,
    get_return_statistics,
    get_returns,
    get_returns_by_customer,
    get_returns_by_sale,
    process_return_to_inventory,
    update_return_status,
)
from utils.auth import get_current_user, get_current_user_from_db, require_permission

router = APIRouter(
    prefix="/returns",
    tags=["returns"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_return_endpoint(
    return_data: ReturnCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_from_db),
):
    """
    Crear una nueva devolución.

    **Requiere:** Usuario autenticado

    **Validaciones:**
    - La venta debe existir y no estar cancelada
    - Los items deben pertenecer a la venta especificada
    - No se puede devolver más cantidad de la comprada
    - Se calcula automáticamente el monto total de reembolso

    **Estado inicial:** `pending` (requiere aprobación)

    **Ejemplo de uso:**
    ```json
    {
      "sale_id": "uuid-de-la-venta",
      "reason": "Producto defectuoso",
      "notes": "El cliente reporta mal funcionamiento",
      "items": [
        {
          "sale_detail_id": "uuid-del-item-vendido",
          "quantity_returned": 2,
          "condition": "damaged"
        }
      ]
    }
    ```
    """
    try:
        user_id = str(current_user.id)
        db_return = create_return(db, return_data, user_id)

        # Obtener detalles completos para la respuesta
        return_details = get_return_full_details(db, str(db_return.id))

        return {
            "message": "Devolución creada exitosamente",
            "return": return_details,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando devolución: {str(e)}",
        )


@router.get("/", response_model=List[dict])
async def get_returns_endpoint(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(
        100, ge=1, le=1000, description="Límite de registros a retornar"
    ),
    status_filter: Optional[str] = Query(
        None, description="Filtrar por estado: pending, approved, rejected, completed"
    ),
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_from_db),
):
    """
    Obtener lista de devoluciones con paginación y filtros.

    **Requiere:** Usuario autenticado

    **Filtros opcionales:**
    - `status`: Filtrar por estado
    - `start_date`: Devoluciones desde esta fecha
    - `end_date`: Devoluciones hasta esta fecha

    **Ordenamiento:** De más reciente a más antigua
    """
    try:
        returns = get_returns(
            db,
            skip=skip,
            limit=limit,
            status=status_filter,
            start_date=start_date,
            end_date=end_date,
        )

        # Construir respuesta con detalles completos
        result = []
        for ret in returns:
            return_details = get_return_full_details(db, str(ret.id))
            if return_details:
                result.append(return_details)

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo devoluciones: {str(e)}",
        )


@router.get("/{return_id}", response_model=dict)
async def get_return_by_id_endpoint(
    return_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_from_db),
):
    """
    Obtener una devolución específica por ID con todos sus detalles.

    **Requiere:** Usuario autenticado

    **Incluye:**
    - Información de la devolución
    - Datos del cliente
    - Usuario que procesó
    - Venta original
    - Items devueltos con nombres de productos
    """
    try:
        return_details = get_return_full_details(db, return_id)
        if not return_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Devolución con ID {return_id} no encontrada",
            )
        return return_details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo devolución: {str(e)}",
        )


@router.get("/code/{return_code}", response_model=dict)
async def get_return_by_code_endpoint(
    return_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_from_db),
):
    """
    Obtener una devolución por su código (ej: DEV-20251104123456).

    **Requiere:** Usuario autenticado
    """
    try:
        return_record = get_return_by_code(db, return_code)
        if not return_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Devolución con código {return_code} no encontrada",
            )

        return_details = get_return_full_details(db, str(return_record.id))
        return return_details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo devolución: {str(e)}",
        )


@router.get("/sale/{sale_id}", response_model=List[dict])
async def get_returns_by_sale_endpoint(
    sale_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_from_db),
):
    """
    Obtener todas las devoluciones de una venta específica.

    **Requiere:** Usuario autenticado

    Útil para ver el historial de devoluciones de una venta.
    """
    try:
        returns = get_returns_by_sale(db, sale_id)

        result = []
        for ret in returns:
            return_details = get_return_full_details(db, str(ret.id))
            if return_details:
                result.append(return_details)

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo devoluciones de la venta: {str(e)}",
        )


@router.get("/customer/{customer_id}", response_model=List[dict])
async def get_returns_by_customer_endpoint(
    customer_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_from_db),
):
    """
    Obtener devoluciones de un cliente específico.

    **Requiere:** Usuario autenticado

    Útil para analizar el comportamiento de devoluciones por cliente.
    """
    try:
        returns = get_returns_by_customer(db, customer_id, skip=skip, limit=limit)

        result = []
        for ret in returns:
            return_details = get_return_full_details(db, str(ret.id))
            if return_details:
                result.append(return_details)

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo devoluciones del cliente: {str(e)}",
        )


@router.put("/{return_id}/status", response_model=dict)
async def update_return_status_endpoint(
    return_id: str,
    status_data: ReturnUpdateStatus,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Entity.PRODUCTS, Action.UPDATE)),
):
    """
    Actualizar el estado de una devolución.

    **Requiere:** ADMIN o SUPERADMIN

    **Transiciones de estado válidas:**
    - `pending` → `approved` o `rejected`
    - `approved` → `completed` o `rejected`
    - `rejected` → (no se puede cambiar)
    - `completed` → (no se puede cambiar)

    **Notas:**
    - Aprobar una devolución no restaura automáticamente el inventario
    - Usar el endpoint `/process` para restaurar el inventario
    """
    try:
        user_id = str(current_user.id)
        updated_return = update_return_status(db, return_id, status_data, user_id)

        return_details = get_return_full_details(db, str(updated_return.id))
        return {
            "message": f"Estado actualizado a '{status_data.status}' exitosamente",
            "return": return_details,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando estado: {str(e)}",
        )


@router.post("/process", response_model=dict)
async def process_return_endpoint(
    request: ReturnProcessRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission(Entity.PRODUCTS, Action.UPDATE)),
):
    """
    Procesar una devolución aprobada y devolver el stock al inventario.

    **Requiere:** ADMIN o SUPERADMIN

    **Validaciones:**
    - La devolución debe estar en estado `approved`
    - Solo productos en condición `good` se devuelven al inventario
    - Productos `damaged` o `expired` no se reintegran

    **Proceso:**
    1. Verifica que la devolución esté aprobada
    2. Restaura el stock según el origen:
       - Si vino de `lot_detail`: incrementa `quantity_available`
       - Si vino de `bulk_conversion`: incrementa `remaining_bulk`
    3. Marca los items como `restocked=True`
    4. Cambia el estado a `completed`

    **Importante:** Este proceso es irreversible
    """
    try:
        processed_return = process_return_to_inventory(db, str(request.return_id))

        return_details = get_return_full_details(db, str(processed_return.id))
        return {
            "message": "Devolución procesada exitosamente. Stock restaurado.",
            "return": return_details,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando devolución: {str(e)}",
        )


@router.post("/{return_id}/process", response_model=dict)
async def process_return_by_id_endpoint(
    return_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission(Entity.PRODUCTS, Action.UPDATE)),
):
    """
    Procesar una devolución aprobada por ID (ruta alternativa).

    **Requiere:** ADMIN o SUPERADMIN

    Este es un endpoint alternativo que acepta el return_id en la URL
    en lugar del body. Funciona idénticamente a POST /returns/process.
    """
    try:
        processed_return = process_return_to_inventory(db, return_id)

        return_details = get_return_full_details(db, str(processed_return.id))
        return {
            "message": "Devolución procesada exitosamente. Stock restaurado.",
            "return": return_details,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando devolución: {str(e)}",
        )


@router.get("/statistics/summary", response_model=ReturnStatsResponse)
async def get_return_statistics_endpoint(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission(Entity.PRODUCTS, Action.READ)),
):
    """
    Obtener estadísticas de devoluciones.

    **Requiere:** Usuario autenticado con permisos de lectura en productos

    **Incluye:**
    - Total de devoluciones
    - Total reembolsado
    - Distribución por estado
    - Distribución por condición de productos
    - Top 10 productos más devueltos

    **Filtros opcionales:**
    - `start_date`: Estadísticas desde esta fecha
    - `end_date`: Estadísticas hasta esta fecha
    """
    try:
        stats = get_return_statistics(db, start_date=start_date, end_date=end_date)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}",
        )
