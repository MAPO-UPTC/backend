import pytest
from unittest.mock import Mock, patch


class TestAuthUtils:
    """Test authentication utilities"""

    def test_active_role_manager_initialization(self):
        """Test ActiveRoleManager initialization"""
        from src.utils.auth import ActiveRoleManager
        
        # ActiveRoleManager uses class variables, so we check class attributes
        assert hasattr(ActiveRoleManager, '_active_roles')
        assert isinstance(ActiveRoleManager._active_roles, dict)

    def test_active_role_manager_set_role(self):
        """Test setting active role"""
        from src.utils.auth import ActiveRoleManager
        from src.constants.role import RoleEnum
        
        user_id = "test_user_123"
        role = RoleEnum.USER
        
        ActiveRoleManager.set_active_role(user_id, role)
        assert ActiveRoleManager.get_active_role(user_id) == role

    def test_active_role_manager_clear_role(self):
        """Test clearing active role"""
        from src.utils.auth import ActiveRoleManager
        from src.constants.role import RoleEnum
        
        user_id = "test_user_123"
        role = RoleEnum.USER
        
        ActiveRoleManager.set_active_role(user_id, role)
        ActiveRoleManager.clear_active_role(user_id)
        assert ActiveRoleManager.get_active_role(user_id) is None

    def test_import_auth_functions(self):
        """Test that auth functions can be imported"""
        from src.utils.auth import get_current_user_from_db, get_user_with_permissions
        
        # These are functions that exist in the auth module
        assert callable(get_current_user_from_db)
        assert callable(get_user_with_permissions)