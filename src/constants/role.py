from enum import Enum
import uuid


class RoleEnum(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPERADMIN = "SUPERADMIN"


class RoleUUID:
    """Mapeo de roles con sus UUIDs específicos"""

    ADMIN = uuid.UUID("6c26db3a-4bf7-4cb8-a0b3-b3ee4765d324")
    SUPERADMIN = uuid.UUID("46f88b8a-f668-41c6-b1ca-23cbfab93127")
    USER = uuid.UUID("2610870b-e576-48f9-9a05-505b00e7daf5")


class RoleManager:
    """Gestor centralizado de roles"""

    # Mapeo rol -> UUID
    ROLE_TO_UUID = {
        RoleEnum.ADMIN: RoleUUID.ADMIN,
        RoleEnum.SUPERADMIN: RoleUUID.SUPERADMIN,
        RoleEnum.USER: RoleUUID.USER,
    }

    # Mapeo UUID -> rol
    UUID_TO_ROLE = {
        RoleUUID.ADMIN: RoleEnum.ADMIN,
        RoleUUID.SUPERADMIN: RoleEnum.SUPERADMIN,
        RoleUUID.USER: RoleEnum.USER,
    }

    @classmethod
    def get_uuid(cls, role: RoleEnum) -> uuid.UUID:
        """Obtiene el UUID de un rol"""
        return cls.ROLE_TO_UUID.get(role)

    @classmethod
    def get_role(cls, role_uuid: uuid.UUID) -> RoleEnum:
        """Obtiene el rol desde un UUID"""
        return cls.UUID_TO_ROLE.get(role_uuid)

    @classmethod
    def get_all_roles(cls) -> list[tuple[RoleEnum, uuid.UUID]]:
        """Obtiene todos los roles con sus UUIDs"""
        return [
            (role, uuid_val) for role, uuid_val in cls.ROLE_TO_UUID.items()
        ]

    @classmethod
    def is_valid_role(cls, role: str) -> bool:
        """Verifica si un rol es válido"""
        try:
            return RoleEnum(role) in cls.ROLE_TO_UUID
        except ValueError:
            return False

    @classmethod
    def get_default_role_uuid(cls) -> uuid.UUID:
        """Obtiene solo el UUID del rol por defecto (USER)"""
        return cls.get_uuid(RoleEnum.USER)

    @classmethod
    def get_default_role(cls) -> tuple[RoleEnum, uuid.UUID]:
        """Obtiene el rol por defecto como tupla (para otros usos)"""
        return RoleEnum.USER, cls.get_uuid(RoleEnum.USER)
