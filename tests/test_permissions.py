import pytest


class TestPermissions:
    """Test permission system"""

    def test_permission_manager_exists(self):
        """Test that PermissionManager can be imported"""
        from src.config.permissions import PermissionManager

        assert PermissionManager is not None

    def test_entity_enum_exists(self):
        """Test that Entity enum can be imported"""
        from src.config.permissions import Entity

        assert hasattr(Entity, "USERS")
        assert hasattr(Entity, "PRODUCTS")

    def test_action_enum_exists(self):
        """Test that Action enum can be imported"""
        from src.config.permissions import Action

        assert hasattr(Action, "CREATE")
        assert hasattr(Action, "READ")
        assert hasattr(Action, "UPDATE")
        assert hasattr(Action, "DELETE")

    def test_permission_level_enum_exists(self):
        """Test that PermissionLevel enum can be imported"""
        from src.config.permissions import PermissionLevel

        assert hasattr(PermissionLevel, "NONE")
        assert hasattr(PermissionLevel, "OWN")
        assert hasattr(PermissionLevel, "ALL")


class TestRoles:
    """Test role system"""

    def test_role_enum_exists(self):
        """Test that RoleEnum can be imported"""
        from src.constants.role import RoleEnum

        assert hasattr(RoleEnum, "USER")
        assert hasattr(RoleEnum, "ADMIN")
        assert hasattr(RoleEnum, "SUPERADMIN")

    def test_role_manager_exists(self):
        """Test that RoleManager can be imported"""
        from src.constants.role import RoleManager

        assert RoleManager is not None
