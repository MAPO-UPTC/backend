from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from config.permissions import Action, Entity, PermissionManager
from database import get_db
from models import get_current_user_roles
from schemas.user import UserResponse
from utils.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtener lista de clientes.
    Los usuarios pueden ver todos los clientes según los permisos.
    """
    # Obtener roles del usuario
    user_roles = get_current_user_roles(current_user.id, db)

    # Verificar permisos para cualquier rol del usuario
    has_permission = False
    for role in user_roles:
        if PermissionManager.can_perform_action(role, Entity.CLIENTS, Action.READ):
            has_permission = True
            break

    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient permissions. Required: CLIENTS READ. User roles: {[role.value for role in user_roles]}",
        )

    # Por ahora devolver array vacío hasta que se implemente la tabla de clientes
    # TODO: Implementar consulta real a la base de datos
    return []


@router.get("/{client_id}", response_model=dict)
async def get_client(
    client_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtener un cliente específico por ID.
    """
    # Obtener roles del usuario
    user_roles = get_current_user_roles(current_user.id, db)

    # Verificar permisos
    has_permission = False
    for role in user_roles:
        if PermissionManager.can_perform_action(role, Entity.CLIENTS, Action.READ):
            has_permission = True
            break

    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient permissions. Required: CLIENTS READ. User roles: {[role.value for role in user_roles]}",
        )

    # Por ahora devolver un cliente de ejemplo
    # TODO: Implementar consulta real a la base de datos
    return {
        "id": client_id,
        "name": "Cliente Ejemplo",
        "email": "cliente@ejemplo.com",
        "phone": "123-456-7890",
    }


@router.post("/", response_model=dict)
async def create_client(
    client_data: dict,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Crear un nuevo cliente.
    """
    # Obtener roles del usuario
    user_roles = get_current_user_roles(current_user.id, db)

    # Verificar permisos
    has_permission = False
    for role in user_roles:
        if PermissionManager.can_perform_action(role, Entity.CLIENTS, Action.CREATE):
            has_permission = True
            break

    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient permissions. Required: CLIENTS CREATE. User roles: {[role.value for role in user_roles]}",
        )

    # TODO: Implementar creación real en la base de datos
    return {
        "message": "Client creation endpoint - implementation pending",
        "data": client_data,
    }
