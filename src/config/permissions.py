from enum import Enum
from typing import Dict, List

from constants.role import RoleEnum


class Action(str, Enum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class Entity(str, Enum):
    USERS = "USERS"
    PRODUCTS = "PRODUCTS"
    SUPPLIERS = "SUPPLIERS"
    CLIENTS = "CLIENTS"
    SALES_ORDERS = "SALES_ORDERS"
    INVENTORY_STOCK = "INVENTORY_STOCK"


class PermissionLevel(str, Enum):
    NONE = "NONE"  # Sin permisos
    OWN = "OWN"  # Solo sus propios datos
    ALL = "ALL"  # Todos los datos
    CONDITIONAL = "CONDITIONAL"  # Condicional (ej: ordenes no emitidas)


# Configuración completa de permisos
PERMISSIONS_CONFIG: Dict[Entity, Dict[Action, Dict[RoleEnum, PermissionLevel]]] = {
    Entity.USERS: {
        Action.CREATE: {
            RoleEnum.USER: PermissionLevel.NONE,
            RoleEnum.ADMIN: PermissionLevel.NONE,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.READ: {
            RoleEnum.USER: PermissionLevel.OWN,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.UPDATE: {
            RoleEnum.USER: PermissionLevel.OWN,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.DELETE: {
            RoleEnum.USER: PermissionLevel.NONE,
            RoleEnum.ADMIN: PermissionLevel.NONE,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
    },
    Entity.PRODUCTS: {
        Action.CREATE: {
            RoleEnum.USER: PermissionLevel.NONE,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.READ: {
            RoleEnum.USER: PermissionLevel.ALL,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.UPDATE: {
            RoleEnum.USER: PermissionLevel.NONE,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.DELETE: {
            RoleEnum.USER: PermissionLevel.NONE,
            RoleEnum.ADMIN: PermissionLevel.NONE,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
    },
    Entity.SUPPLIERS: {
        Action.CREATE: {
            RoleEnum.USER: PermissionLevel.NONE,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.READ: {
            RoleEnum.USER: PermissionLevel.NONE,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.UPDATE: {
            RoleEnum.USER: PermissionLevel.NONE,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.DELETE: {
            RoleEnum.USER: PermissionLevel.NONE,
            RoleEnum.ADMIN: PermissionLevel.NONE,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
    },
    Entity.CLIENTS: {
        Action.CREATE: {
            RoleEnum.USER: PermissionLevel.ALL,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.READ: {
            RoleEnum.USER: PermissionLevel.ALL,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.UPDATE: {
            RoleEnum.USER: PermissionLevel.OWN,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.DELETE: {
            RoleEnum.USER: PermissionLevel.NONE,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
    },
    Entity.SALES_ORDERS: {
        Action.CREATE: {
            RoleEnum.USER: PermissionLevel.NONE,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.READ: {
            RoleEnum.USER: PermissionLevel.OWN,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.UPDATE: {
            RoleEnum.USER: PermissionLevel.NONE,
            RoleEnum.ADMIN: PermissionLevel.CONDITIONAL,  # Solo si no está emitida
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.DELETE: {
            RoleEnum.USER: PermissionLevel.NONE,
            RoleEnum.ADMIN: PermissionLevel.NONE,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
    },
    Entity.INVENTORY_STOCK: {
        Action.CREATE: {
            RoleEnum.USER: PermissionLevel.NONE,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.READ: {
            RoleEnum.USER: PermissionLevel.ALL,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.UPDATE: {
            RoleEnum.USER: PermissionLevel.NONE,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
        Action.DELETE: {
            RoleEnum.USER: PermissionLevel.NONE,
            RoleEnum.ADMIN: PermissionLevel.ALL,
            RoleEnum.SUPERADMIN: PermissionLevel.ALL,
        },
    },
}


class PermissionManager:
    """Gestor de permisos basado en roles"""

    @staticmethod
    def has_permission(
        role: RoleEnum, entity: Entity, action: Action
    ) -> PermissionLevel:
        """
        Verifica si un rol tiene permiso para realizar una acción en una entidad.
        Retorna el nivel de permiso.
        """
        try:
            return PERMISSIONS_CONFIG[entity][action][role]
        except KeyError:
            return PermissionLevel.NONE

    @staticmethod
    def can_perform_action(role: RoleEnum, entity: Entity, action: Action) -> bool:
        """
        Verifica si un rol puede realizar una acción (cualquier nivel excepto NONE).
        """
        permission_level = PermissionManager.has_permission(role, entity, action)
        return permission_level != PermissionLevel.NONE

    @staticmethod
    def get_user_permissions(role: RoleEnum) -> Dict[str, Dict[str, str]]:
        """
        Obtiene todos los permisos de un usuario para enviar al frontend.
        """
        permissions = {}

        for entity in Entity:
            permissions[entity.value] = {}
            for action in Action:
                permission_level = PermissionManager.has_permission(
                    role, entity, action
                )
                permissions[entity.value][action.value] = permission_level.value

        return permissions

    @staticmethod
    def get_allowed_entities_for_action(role: RoleEnum, action: Action) -> List[Entity]:
        """
        Obtiene todas las entidades en las que un rol puede realizar una acción específica.
        """
        allowed_entities = []

        for entity in Entity:
            if PermissionManager.can_perform_action(role, entity, action):
                allowed_entities.append(entity)

        return allowed_entities
