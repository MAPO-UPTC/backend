import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.main import app

@pytest.fixture
def client():
    """Test client fixture for FastAPI app"""
    return TestClient(app)

@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "name": "Test",
        "last_name": "User",
        "document_type": "CC",
        "document_number": "12345678",
        "email": "test@example.com",
        "password": "testpass123"
    }

@pytest.fixture
def test_product_data():
    """Sample product data for testing"""
    return {
        "name": "Test Product",
        "description": "A test product",
        "price": 29.99,
        "stock": 100,
        "category": "Test Category",
        "image_url": "https://example.com/image.jpg"
    }