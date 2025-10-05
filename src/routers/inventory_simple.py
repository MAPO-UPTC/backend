"""
Router básico para inventario
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from utils.auth import get_current_user
from schemas.user import UserResponse

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_inventory_stock(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtener lista básica de inventario
    """
    return [
        {
            "id": 1,
            "product_name": "Comida para perros",
            "presentation": "20kg",
            "stock": 50,
            "last_updated": "2024-01-01T10:00:00Z"
        }
    ]