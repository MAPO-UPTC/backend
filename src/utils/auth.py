from fastapi import HTTPException, Request
from firebase_admin import auth as admin_auth
from sqlalchemy.orm import Session
from database import engine
from models_db import User, Person, UserRole, Role
from constants.role import RoleManager, RoleEnum
from config.permissions import PermissionManager, Entity, Action, PermissionLevel

import sys
import os
from typing import Dict, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# En-memory storage para roles activos de usuarios


class ActiveRoleManager:
    """
    Gestor de roles activos para usuarios.
    Mantiene en memoria qué rol está usando cada usuario actualmente.
    """

    _active_roles: Dict[str, RoleEnum] = {}

    @classmethod
    def set_active_role(cls, user_id: str, role: RoleEnum) -> None:
        """Establecer el rol activo para un usuario."""
        cls._active_roles[user_id] = role

    @classmethod
    def get_active_role(cls, user_id: str) -> Optional[RoleEnum]:
        """Obtener el rol activo de un usuario."""
        return cls._active_roles.get(user_id)

    @classmethod
    def clear_active_role(cls, user_id: str) -> None:
        """Limpiar el rol activo de un usuario."""
        if user_id in cls._active_roles:
            del cls._active_roles[user_id]

    @classmethod
    def has_active_role(cls, user_id: str) -> bool:
        """Verificar si un usuario tiene un rol activo establecido."""
        return user_id in cls._active_roles


def get_current_user(request: Request):
    """
    Dependencia para validar el token de Firebase y obtener el usuario actual.
    """
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    # Extraer el token del header "Bearer <token>"
    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        # Si no hay espacio, asumir que es solo el token
        token = authorization

    try:
        decoded_token = admin_auth.verify_id_token(token)
        return decoded_token
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user_from_db(request: Request):
    """
    Dependencia que obtiene el usuario completo 
    desde la base de datos con sus roles.
    """
    decoded_token = get_current_user(request)
    uid = decoded_token.get("uid")

    with Session(engine) as session:
        user = session.query(User).join(Person).filter(User.uid == uid).first()
        if not user:
            raise HTTPException(
                status_code=404, detail="User not found in database")

        # Obtener roles del usuario
        user_roles = session.query(UserRole).filter_by(user_id=user.id).all()
        roles = []

        for user_role in user_roles:
            role = session.query(Role).filter_by(id=user_role.role_id).first()
            if role:
                role_enum = RoleManager.get_role(role.id)
                if role_enum:
                    roles.append(role_enum)

        # Agregar roles al objeto user
        user.roles = roles
        return user


def get_effective_roles(user, user_id: str) -> list[RoleEnum]:
    """
    Obtener los roles efectivos del usuario.
    Si tiene un rol activo, usar solo ese. Si no, usar todos sus roles.
    """
    active_role = ActiveRoleManager.get_active_role(user_id)

    if active_role and active_role in user.roles:
        return [active_role]
    else:
        # Si no hay rol activo o el rol activo no está 
        # en sus roles disponibles,
        # usar todos los roles
        return user.roles


def require_permission(entity: Entity, action: Action, allow_own: bool = False):
    """
    Dependencia para verificar que el usuario tenga permiso para realizar una acción.
    Considera el rol activo del usuario si está establecido.

    Args:
        entity: La entidad sobre la que se quiere actuar
        action: La acción que se quiere realizar
        allow_own: Si se permite acceso a datos propios cuando el permiso es OWN
    """

    def permission_checker(request: Request):
        user = get_current_user_from_db(request)
        user_id = str(user.id)

        # Obtener roles efectivos (rol activo si existe, o todos los roles)
        effective_roles = get_effective_roles(user, user_id)

        # Verificar permisos para los roles efectivos
        has_permission = False
        permission_level = PermissionLevel.NONE

        for role in effective_roles:
            level = PermissionManager.has_permission(role, entity, action)
            if level == PermissionLevel.ALL:
                has_permission = True
                permission_level = PermissionLevel.ALL
                break
            elif level == PermissionLevel.OWN and allow_own:
                has_permission = True
                permission_level = PermissionLevel.OWN
            elif level == PermissionLevel.CONDITIONAL:
                has_permission = True
                permission_level = PermissionLevel.CONDITIONAL

        if not has_permission:
            active_role = ActiveRoleManager.get_active_role(user_id)
            if active_role:
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions with active role '{active_role.value}'. Required: {entity.value} {action.value}",
                )
            else:
                role_names = [role.value for role in effective_roles]
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Required: {entity.value} {action.value}. User roles: {role_names}",
                )

        # Agregar información de permisos al usuario
        user.permission_level = permission_level
        user.effective_roles = effective_roles
        return user

    return permission_checker


def get_user_with_permissions(request: Request):
    """
    Dependencia que obtiene el usuario con sus permisos calculados.
    Considera el rol activo si está establecido.
    """
    user = get_current_user_from_db(request)
    user_id = str(user.id)

    # Obtener roles efectivos (rol activo si existe, o todos los roles)
    effective_roles = get_effective_roles(user, user_id)

    # Calcular permisos para los roles efectivos
    all_permissions = {}

    for role in effective_roles:
        role_permissions = PermissionManager.get_user_permissions(role)

        # Combinar permisos (tomar el más alto)
        for entity, actions in role_permissions.items():
            if entity not in all_permissions:
                all_permissions[entity] = {}

            for action, level in actions.items():
                current_level = all_permissions[entity].get(
                    action, PermissionLevel.NONE.value
                )

                # Jerarquía: ALL > CONDITIONAL > OWN > NONE
                if level == PermissionLevel.ALL.value:
                    all_permissions[entity][action] = level
                elif (
                    level == PermissionLevel.CONDITIONAL.value
                    and current_level != PermissionLevel.ALL.value
                ):
                    all_permissions[entity][action] = level
                elif level == PermissionLevel.OWN.value and current_level in [
                    PermissionLevel.NONE.value,
                    PermissionLevel.OWN.value,
                ]:
                    all_permissions[entity][action] = level

    # Agregar información adicional al usuario
    user.permissions = all_permissions
    user.effective_roles = effective_roles
    user.active_role = ActiveRoleManager.get_active_role(user_id)
    return user


def split_full_name(full_name: str):
    """
    Función para separar nombre completo en partes individuales.
    Maneja casos con paréntesis y nombres opcionales.
    """
    # Divide y limpia cada parte
    parts = [p.replace("(", "").replace(")", "")
             for p in full_name.strip().split()]
    # Elimina partes vacías
    parts = [p for p in parts if p]

    first_name = parts[0] if len(parts) > 0 else ""
    second_first_name = parts[1] if len(parts) > 3 else None
    last_name = parts[-2] if len(parts) > 2 else (parts[1]
                                                  if len(parts) == 2 else "")
    second_last_name = parts[-1] if len(parts) > 2 else None

    return first_name, second_first_name, last_name, second_last_name
