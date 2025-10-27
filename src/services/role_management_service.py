"""
Servicio para gestión de roles y permisos de usuarios
Solo accesible para SUPERADMIN
"""

import uuid
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from constants.role import RoleEnum, RoleManager
from database import engine
from models_db import Person, Role, User, UserRole
from schemas.role_management import UserRoleInfo


def get_all_users_with_roles() -> List[UserRoleInfo]:
    """
    Obtener todos los usuarios con sus roles asignados
    Solo para SUPERADMIN
    """
    with Session(engine) as session:
        users = session.query(User).options(selectinload(User.person)).all()

        users_info = []
        for user in users:
            # Obtener roles del usuario
            user_roles = session.query(UserRole).filter_by(user_id=user.id).all()
            roles = []

            for user_role in user_roles:
                role = session.query(Role).filter_by(id=user_role.role_id).first()
                if role:
                    role_enum = RoleManager.get_role(role.id)
                    if role_enum:
                        roles.append(role_enum.value)

            users_info.append(
                UserRoleInfo(
                    user_id=user.id,
                    email=user.email,
                    name=user.person.name,
                    last_name=user.person.last_name,
                    document_type=user.person.document_type,
                    document_number=user.person.document_number,
                    roles=roles,
                )
            )

        return users_info


def get_user_roles_by_id(user_id: str) -> UserRoleInfo:
    """
    Obtener roles de un usuario específico
    Solo para SUPERADMIN
    """
    with Session(engine) as session:
        user = (
            session.query(User)
            .options(selectinload(User.person))
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Obtener roles del usuario
        user_roles = session.query(UserRole).filter_by(user_id=user.id).all()
        roles = []

        for user_role in user_roles:
            role = session.query(Role).filter_by(id=user_role.role_id).first()
            if role:
                role_enum = RoleManager.get_role(role.id)
                if role_enum:
                    roles.append(role_enum.value)

        return UserRoleInfo(
            user_id=user.id,
            email=user.email,
            name=user.person.name,
            last_name=user.person.last_name,
            document_type=user.person.document_type,
            document_number=user.person.document_number,
            roles=roles,
        )


def assign_role_to_user(user_id: str, role_name: str) -> dict:
    """
    Asignar un rol a un usuario
    Solo para SUPERADMIN

    Args:
        user_id: ID del usuario
        role_name: Nombre del rol (USER, ADMIN, SUPERADMIN)

    Returns:
        dict con información del usuario actualizado
    """
    with Session(engine) as session:
        # Verificar que el usuario existe
        user = (
            session.query(User)
            .options(selectinload(User.person))
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Validar que el rol existe
        try:
            role_enum = RoleEnum(role_name)
        except ValueError:
            valid_roles = [r.value for r in RoleEnum]
            raise HTTPException(
                status_code=400,
                detail=f"Rol inválido: {role_name}. Roles válidos: {valid_roles}",
            )

        # Obtener el UUID del rol
        role_uuid = RoleManager.get_uuid(role_enum)
        if not role_uuid:
            raise HTTPException(
                status_code=500, detail=f"No se pudo obtener UUID para rol {role_name}"
            )

        # Verificar si el usuario ya tiene este rol
        existing_role = (
            session.query(UserRole)
            .filter_by(user_id=user.id, role_id=role_uuid)
            .first()
        )

        if existing_role:
            raise HTTPException(
                status_code=400,
                detail=f"El usuario ya tiene el rol {role_name} asignado",
            )

        # Asignar el rol
        new_user_role = UserRole(user_id=user.id, role_id=role_uuid)
        session.add(new_user_role)
        session.commit()

        # Obtener todos los roles actualizados del usuario
        user_roles = session.query(UserRole).filter_by(user_id=user.id).all()
        roles = []

        for ur in user_roles:
            role = session.query(Role).filter_by(id=ur.role_id).first()
            if role:
                role_enum_obj = RoleManager.get_role(role.id)
                if role_enum_obj:
                    roles.append(role_enum_obj.value)

        return {
            "user_id": str(user.id),
            "email": user.email,
            "name": user.person.name,
            "last_name": user.person.last_name,
            "roles": roles,
            "message": f"Rol {role_name} asignado exitosamente",
        }


def remove_role_from_user(user_id: str, role_name: str) -> dict:
    """
    Remover un rol de un usuario
    Solo para SUPERADMIN

    Args:
        user_id: ID del usuario
        role_name: Nombre del rol a remover

    Returns:
        dict con información del usuario actualizado
    """
    with Session(engine) as session:
        # Verificar que el usuario existe
        user = (
            session.query(User)
            .options(selectinload(User.person))
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Validar que el rol existe
        try:
            role_enum = RoleEnum(role_name)
        except ValueError:
            valid_roles = [r.value for r in RoleEnum]
            raise HTTPException(
                status_code=400,
                detail=f"Rol inválido: {role_name}. Roles válidos: {valid_roles}",
            )

        # Obtener el UUID del rol
        role_uuid = RoleManager.get_uuid(role_enum)
        if not role_uuid:
            raise HTTPException(
                status_code=500, detail=f"No se pudo obtener UUID para rol {role_name}"
            )

        # Verificar que el usuario tiene este rol
        user_role = (
            session.query(UserRole)
            .filter_by(user_id=user.id, role_id=role_uuid)
            .first()
        )

        if not user_role:
            raise HTTPException(
                status_code=400,
                detail=f"El usuario no tiene el rol {role_name} asignado",
            )

        # Verificar que el usuario no se quede sin roles
        total_roles = session.query(UserRole).filter_by(user_id=user.id).count()

        if total_roles <= 1:
            raise HTTPException(
                status_code=400,
                detail="No se puede remover el único rol del usuario. "
                "Asigne otro rol antes de remover este.",
            )

        # Protección especial: no permitir remover SUPERADMIN del último SUPERADMIN
        if role_enum == RoleEnum.SUPERADMIN:
            # Contar cuántos SUPERADMIN hay en total
            superadmin_count = (
                session.query(UserRole).filter_by(role_id=role_uuid).count()
            )

            if superadmin_count <= 1:
                raise HTTPException(
                    status_code=400,
                    detail="No se puede remover el rol SUPERADMIN del único "
                    "SUPERADMIN del sistema. Debe haber al menos un SUPERADMIN.",
                )

        # Remover el rol
        session.delete(user_role)
        session.commit()

        # Obtener roles actualizados del usuario
        user_roles = session.query(UserRole).filter_by(user_id=user.id).all()
        roles = []

        for ur in user_roles:
            role = session.query(Role).filter_by(id=ur.role_id).first()
            if role:
                role_enum_obj = RoleManager.get_role(role.id)
                if role_enum_obj:
                    roles.append(role_enum_obj.value)

        return {
            "user_id": str(user.id),
            "email": user.email,
            "name": user.person.name,
            "last_name": user.person.last_name,
            "roles": roles,
            "message": f"Rol {role_name} removido exitosamente",
        }


def set_user_roles(user_id: str, roles: List[str]) -> dict:
    """
    Establecer los roles de un usuario (reemplaza todos los roles actuales)
    Solo para SUPERADMIN

    Args:
        user_id: ID del usuario
        roles: Lista de nombres de roles

    Returns:
        dict con información del usuario actualizado
    """
    with Session(engine) as session:
        # Verificar que el usuario existe
        user = (
            session.query(User)
            .options(selectinload(User.person))
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Validar que hay al menos un rol
        if not roles or len(roles) == 0:
            raise HTTPException(
                status_code=400, detail="Debe proporcionar al menos un rol"
            )

        # Validar todos los roles
        role_enums = []
        role_uuids = []

        for role_name in roles:
            try:
                role_enum = RoleEnum(role_name)
                role_enums.append(role_enum)

                role_uuid = RoleManager.get_uuid(role_enum)
                if not role_uuid:
                    raise HTTPException(
                        status_code=500,
                        detail=f"No se pudo obtener UUID para rol {role_name}",
                    )
                role_uuids.append(role_uuid)

            except ValueError:
                valid_roles = [r.value for r in RoleEnum]
                raise HTTPException(
                    status_code=400,
                    detail=f"Rol inválido: {role_name}. Roles válidos: {valid_roles}",
                )

        # Eliminar todos los roles actuales del usuario
        session.query(UserRole).filter_by(user_id=user.id).delete()

        # Asignar los nuevos roles
        for role_uuid in role_uuids:
            new_user_role = UserRole(user_id=user.id, role_id=role_uuid)
            session.add(new_user_role)

        session.commit()

        return {
            "user_id": str(user.id),
            "email": user.email,
            "name": user.person.name,
            "last_name": user.person.last_name,
            "roles": [r.value for r in role_enums],
            "message": "Roles actualizados exitosamente",
        }
