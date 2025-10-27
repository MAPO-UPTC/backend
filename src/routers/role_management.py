"""
Router para gestión de roles y permisos
Solo accesible para usuarios con rol SUPERADMIN
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from config.permissions import Entity, PermissionLevel, PermissionManager
from constants.role import RoleEnum
from schemas.role_management import (
    AllUsersRolesResponse,
    AssignRoleRequest,
    RemoveRoleRequest,
    UserRoleInfo,
    UserRolesResponse,
)
from services.role_management_service import (
    assign_role_to_user,
    get_all_users_with_roles,
    get_user_roles_by_id,
    remove_role_from_user,
    set_user_roles,
)
from utils.auth import get_user_with_permissions

router = APIRouter(
    prefix="/role-management",
    tags=["role-management"],
    responses={404: {"description": "Not found"}},
)


def require_superadmin(user=Depends(get_user_with_permissions)):
    """
    Dependency para verificar que el usuario es SUPERADMIN
    """
    # Verificar si el usuario tiene rol SUPERADMIN en sus roles efectivos
    if RoleEnum.SUPERADMIN not in user.effective_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los usuarios con rol SUPERADMIN pueden gestionar roles. "
            f"Tus roles actuales: {[r.value for r in user.effective_roles]}",
        )
    return user


@router.get("/users", response_model=AllUsersRolesResponse)
async def get_all_users_roles(current_user=Depends(require_superadmin)):
    """
    Obtener todos los usuarios con sus roles asignados

    **Requiere:** Rol SUPERADMIN

    **Retorna:**
    - Lista de todos los usuarios del sistema
    - Información básica de cada usuario (email, nombre, documento)
    - Roles asignados a cada usuario

    **Ejemplo de respuesta:**
    ```json
    {
      "users": [
        {
          "user_id": "uuid",
          "email": "user@example.com",
          "name": "Juan",
          "last_name": "Pérez",
          "document_type": "CC",
          "document_number": "1234567890",
          "roles": ["USER", "ADMIN"]
        }
      ],
      "total": 10
    }
    ```
    """
    try:
        users = get_all_users_with_roles()
        return AllUsersRolesResponse(users=users, total=len(users))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo usuarios: {str(e)}",
        )


@router.get("/users/{user_id}", response_model=UserRoleInfo)
async def get_user_roles(user_id: uuid.UUID, current_user=Depends(require_superadmin)):
    """
    Obtener roles de un usuario específico

    **Requiere:** Rol SUPERADMIN

    **Parámetros:**
    - `user_id`: UUID del usuario

    **Retorna:**
    - Información del usuario
    - Roles asignados

    **Ejemplo de respuesta:**
    ```json
    {
      "user_id": "uuid",
      "email": "user@example.com",
      "name": "Juan",
      "last_name": "Pérez",
      "document_type": "CC",
      "document_number": "1234567890",
      "roles": ["USER", "ADMIN"]
    }
    ```
    """
    try:
        return get_user_roles_by_id(str(user_id))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo roles del usuario: {str(e)}",
        )


@router.post("/assign-role", response_model=UserRolesResponse)
async def assign_role(
    request: AssignRoleRequest, current_user=Depends(require_superadmin)
):
    """
    Asignar un rol a un usuario

    **Requiere:** Rol SUPERADMIN

    **Roles disponibles:**
    - `USER`: Usuario básico (permisos limitados)
    - `ADMIN`: Administrador (permisos amplios)
    - `SUPERADMIN`: Super administrador (todos los permisos)

    **Request body:**
    ```json
    {
      "user_id": "uuid-del-usuario",
      "role": "ADMIN"
    }
    ```

    **Validaciones:**
    - El usuario debe existir
    - El rol debe ser válido
    - El usuario no debe tener ya ese rol asignado

    **Retorna:**
    - Información actualizada del usuario
    - Lista de todos los roles del usuario
    - Mensaje de confirmación
    """
    try:
        result = assign_role_to_user(str(request.user_id), request.role)
        return UserRolesResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error asignando rol: {str(e)}",
        )


@router.post("/remove-role", response_model=UserRolesResponse)
async def remove_role(
    request: RemoveRoleRequest, current_user=Depends(require_superadmin)
):
    """
    Remover un rol de un usuario

    **Requiere:** Rol SUPERADMIN

    **Request body:**
    ```json
    {
      "user_id": "uuid-del-usuario",
      "role": "ADMIN"
    }
    ```

    **Validaciones:**
    - El usuario debe existir
    - El usuario debe tener el rol asignado
    - El usuario no puede quedar sin roles (mínimo 1 rol)
    - No se puede remover SUPERADMIN si es el único SUPERADMIN del sistema

    **Protecciones de seguridad:**
    - Siempre debe haber al menos un SUPERADMIN en el sistema
    - Un usuario siempre debe tener al menos un rol

    **Retorna:**
    - Información actualizada del usuario
    - Lista de roles restantes del usuario
    - Mensaje de confirmación
    """
    try:
        result = remove_role_from_user(str(request.user_id), request.role)
        return UserRolesResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removiendo rol: {str(e)}",
        )


@router.put("/users/{user_id}/roles", response_model=UserRolesResponse)
async def update_user_roles(
    user_id: uuid.UUID, roles: List[str], current_user=Depends(require_superadmin)
):
    """
    Actualizar todos los roles de un usuario (reemplaza roles existentes)

    **Requiere:** Rol SUPERADMIN

    **Parámetros:**
    - `user_id`: UUID del usuario
    - `roles`: Array con los nuevos roles (reemplaza todos los anteriores)

    **Request body:**
    ```json
    ["USER", "ADMIN"]
    ```

    **Validaciones:**
    - El usuario debe existir
    - Debe proporcionar al menos un rol
    - Todos los roles deben ser válidos

    **Nota:** Esta operación reemplaza TODOS los roles actuales del usuario
    con los proporcionados en la lista.

    **Retorna:**
    - Información actualizada del usuario
    - Nueva lista de roles
    - Mensaje de confirmación
    """
    try:
        result = set_user_roles(str(user_id), roles)
        return UserRolesResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando roles: {str(e)}",
        )


@router.get("/available-roles")
async def get_available_roles(current_user=Depends(require_superadmin)):
    """
    Obtener lista de roles disponibles en el sistema

    **Requiere:** Rol SUPERADMIN

    **Retorna:**
    - Lista de roles disponibles
    - Descripción de cada rol

    **Ejemplo de respuesta:**
    ```json
    {
      "roles": [
        {
          "name": "USER",
          "description": "Usuario básico con permisos limitados"
        },
        {
          "name": "ADMIN",
          "description": "Administrador con permisos amplios"
        },
        {
          "name": "SUPERADMIN",
          "description": "Super administrador con todos los permisos"
        }
      ]
    }
    ```
    """
    return {
        "roles": [
            {
                "name": RoleEnum.USER.value,
                "description": "Usuario básico con permisos limitados. "
                "Puede ver productos, crear clientes y ver sus propias ventas.",
            },
            {
                "name": RoleEnum.ADMIN.value,
                "description": "Administrador con permisos amplios. "
                "Puede gestionar productos, proveedores, inventario y todas las ventas.",
            },
            {
                "name": RoleEnum.SUPERADMIN.value,
                "description": "Super administrador con todos los permisos. "
                "Puede gestionar usuarios, roles y tiene acceso completo al sistema.",
            },
        ]
    }


@router.get("/my-permissions")
async def get_my_permissions_details(current_user=Depends(require_superadmin)):
    """
    Obtener información detallada de los permisos del SUPERADMIN actual

    **Requiere:** Rol SUPERADMIN

    **Retorna:**
    - Información del usuario
    - Roles asignados
    - Permisos detallados por entidad y acción

    Útil para debugging y verificación de permisos.
    """
    return {
        "user_id": str(current_user.id),
        "email": current_user.email,
        "roles": [role.value for role in current_user.effective_roles],
        "active_role": (
            current_user.active_role.value if current_user.active_role else None
        ),
        "permissions": current_user.permissions,
    }
