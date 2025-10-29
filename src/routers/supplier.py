"""
Router para manejo de proveedores
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from config.permissions import Action, Entity
from database import get_db
from schemas.supplier import SupplierCreate, SupplierResponse, SupplierUpdate
from services.supplier_service import (
    create_supplier,
    delete_supplier,
    get_supplier_by_id,
    get_suppliers,
    update_supplier,
)
from utils.auth import get_current_user, require_permission

router = APIRouter(
    prefix="/suppliers",
    tags=["suppliers"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=SupplierResponse)
async def create_supplier_endpoint(
    supplier: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission(Entity.PRODUCTS, Action.CREATE)),
):
    """
    Crear un nuevo proveedor.
    Solo ADMIN y SUPERADMIN pueden crear proveedores.
    """
    try:
        db_supplier = create_supplier(db, supplier)
        return db_supplier
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando proveedor: {str(e)}",
        )


@router.get("/", response_model=List[SupplierResponse])
async def get_suppliers_endpoint(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(
        100, ge=1, le=1000, description="Límite de registros a retornar"
    ),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Obtener lista de proveedores con paginación.
    Endpoint público para usuarios autenticados.
    """
    try:
        suppliers = get_suppliers(db, skip=skip, limit=limit)
        return suppliers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo proveedores: {str(e)}",
        )


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier_by_id_endpoint(
    supplier_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Obtener un proveedor específico por ID.
    Endpoint público para usuarios autenticados.
    """
    try:
        supplier = get_supplier_by_id(db, supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proveedor con ID {supplier_id} no encontrado",
            )
        return supplier
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo proveedor: {str(e)}",
        )


@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier_endpoint(
    supplier_id: str,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission(Entity.PRODUCTS, Action.UPDATE)),
):
    """
    Actualizar un proveedor existente.
    Solo ADMIN y SUPERADMIN pueden actualizar proveedores.
    """
    try:
        updated_supplier = update_supplier(db, supplier_id, supplier_data)
        return updated_supplier
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando proveedor: {str(e)}",
        )


@router.delete("/{supplier_id}")
async def delete_supplier_endpoint(
    supplier_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission(Entity.PRODUCTS, Action.DELETE)),
):
    """
    Eliminar un proveedor.
    Solo SUPERADMIN puede eliminar proveedores.
    """
    try:
        result = delete_supplier(db, supplier_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando proveedor: {str(e)}",
        )
