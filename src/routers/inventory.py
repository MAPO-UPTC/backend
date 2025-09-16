from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from config.permissions import Entity, Action, PermissionManager
from database import get_db
from models import get_current_user_roles
from schemas.user import UserResponse
from utils.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_inventory_stock(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtener lista de inventario/stock.
    Los usuarios pueden ver todo el inventario según los permisos.
    """
    # Obtener roles del usuario
    user_roles = get_current_user_roles(current_user.id, db)

    # Verificar permisos para cualquier rol del usuario
    has_permission = False
    for role in user_roles:
        if PermissionManager.can_perform_action(
            role, Entity.INVENTORY_STOCK, Action.READ
        ):
            has_permission = True
            break

    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient permissions. Required: INVENTORY_STOCK READ. User roles: {[role.value for role in user_roles]}",
        )

    # Por ahora devolver array vacío hasta que se implemente la tabla de inventario
    # TODO: Implementar consulta real a la base de datos
    return []


@router.get("/{inventory_id}", response_model=dict)
async def get_inventory_item(
    inventory_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtener un elemento de inventario específico por ID.
    """
    # Obtener roles del usuario
    user_roles = get_current_user_roles(current_user.id, db)

    # Verificar permisos
    has_permission = False
    for role in user_roles:
        if PermissionManager.can_perform_action(
            role, Entity.INVENTORY_STOCK, Action.READ
        ):
            has_permission = True
            break

    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient permissions. Required: INVENTORY_STOCK READ. User roles: {[role.value for role in user_roles]}",
        )

    # Por ahora devolver un item de inventario de ejemplo
    # TODO: Implementar consulta real a la base de datos
    return {
        "id": inventory_id,
        "product_id": "example-product-id",
        "quantity": 100,
        "location": "Warehouse A",
        "last_updated": "2025-09-16T06:00:00Z",
    }


@router.post("/", response_model=dict)
async def create_inventory_item(
    inventory_data: dict,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Crear un nuevo elemento de inventario.
    """
    # Obtener roles del usuario
    user_roles = get_current_user_roles(current_user.id, db)

    # Verificar permisos
    has_permission = False
    for role in user_roles:
        if PermissionManager.can_perform_action(
            role, Entity.INVENTORY_STOCK, Action.CREATE
        ):
            has_permission = True
            break

    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient permissions. Required: INVENTORY_STOCK CREATE. User roles: {[role.value for role in user_roles]}",
        )

    # TODO: Implementar creación real en la base de datos
    return {
        "message": "Inventory creation endpoint - implementation pending",
        "data": inventory_data,
    }
