from fastapi import APIRouter, Depends
from schemas.product import ProductCreate, ProductUpdate, ProductResponse
from services.product_service import (
    create_product_service,
    get_products_service,
    get_product_by_id_service,
    update_product_service,
    delete_product_service
)
from utils.auth import get_current_user
from typing import List
import uuid

router = APIRouter()

@router.post("/", response_model=dict)
async def create_product(
    product_data: ProductCreate,
    current_user=Depends(get_current_user)
):
    """
    Crear un nuevo producto (requiere autenticación).
    """
    return create_product_service(product_data)

@router.get("/", response_model=List[dict])
async def get_products():
    """
    Obtener todos los productos.
    """
    return get_products_service()

@router.get("/{product_id}", response_model=dict)
async def get_product(product_id: uuid.UUID):
    """
    Obtener un producto por ID.
    """
    return get_product_by_id_service(product_id)

@router.put("/{product_id}", response_model=dict)
async def update_product(
    product_id: uuid.UUID,
    product_data: ProductUpdate,
    current_user=Depends(get_current_user)
):
    """
    Actualizar un producto (requiere autenticación).
    """
    return update_product_service(product_id, product_data)

@router.delete("/{product_id}")
async def delete_product(
    product_id: uuid.UUID,
    current_user=Depends(get_current_user)
):
    """
    Eliminar un producto (requiere autenticación).
    """
    return delete_product_service(product_id)