"""
Esquemas para gestión de roles y permisos
"""

import uuid
from typing import List, Optional

from pydantic import BaseModel, Field


class UserRoleInfo(BaseModel):
    """Información básica de un usuario con sus roles"""

    user_id: uuid.UUID
    email: str
    name: str
    last_name: str
    document_type: str
    document_number: str
    roles: List[str] = Field(default=[], description="Lista de roles asignados al usuario")

    class Config:
        from_attributes = True


class AssignRoleRequest(BaseModel):
    """Request para asignar un rol a un usuario"""

    user_id: uuid.UUID = Field(..., description="ID del usuario al que se asignará el rol")
    role: str = Field(..., description="Rol a asignar (USER, ADMIN, SUPERADMIN)")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "role": "ADMIN"
            }
        }


class RemoveRoleRequest(BaseModel):
    """Request para remover un rol de un usuario"""

    user_id: uuid.UUID = Field(..., description="ID del usuario al que se removerá el rol")
    role: str = Field(..., description="Rol a remover (USER, ADMIN, SUPERADMIN)")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "role": "ADMIN"
            }
        }


class UserRolesResponse(BaseModel):
    """Respuesta con roles actualizados de un usuario"""

    user_id: uuid.UUID
    email: str
    name: str
    last_name: str
    roles: List[str]
    message: str

    class Config:
        from_attributes = True


class AllUsersRolesResponse(BaseModel):
    """Respuesta con todos los usuarios y sus roles"""

    users: List[UserRoleInfo]
    total: int

    class Config:
        from_attributes = True


class RoleValidationResponse(BaseModel):
    """Respuesta de validación de roles"""

    valid: bool
    role: Optional[str] = None
    message: str
