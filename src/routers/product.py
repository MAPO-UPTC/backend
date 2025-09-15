from fastapi import APIRouter, Depends
from schemas.product import ProductCreate, ProductUpdate
from services.product_service import (
    create_product_service,
    get_products_service,
    get_product_by_id_service,
    update_product_service,
    delete_product_service,
)
from utils.auth import require_permission
from config.permissions import Entity, Action
from typing import List
import uuid

router = APIRouter()


@router.post("/", response_model=dict)
async def create_product(
    product_data: ProductCreate,
    current_user=Depends(require_permission(Entity.PRODUCTS, Action.CREATE)),
):
    """
    Crear producto - Solo ADMIN y SUPERADMIN pueden crear productos.
    """
    print(f"Received product data: {product_data}")
    return create_product_service(product_data)


@router.get("/", response_model=List[dict])
async def get_products():
    """
    Obtener todos los productos (público).
    """
    return get_products_service()


@router.get("/{product_id}", response_model=dict)
async def get_product(product_id: uuid.UUID):
    """
    Obtener un producto por ID (público).
    """
    return get_product_by_id_service(product_id)


@router.put("/{product_id}", response_model=dict)
async def update_product(
    product_id: uuid.UUID,
    product_data: ProductUpdate,
    current_user=Depends(require_permission(Entity.PRODUCTS, Action.UPDATE)),
):
    """
    Actualizar producto - Solo ADMIN y SUPERADMIN pueden actualizar productos.
    """
    return update_product_service(product_id, product_data)


@router.delete("/{product_id}")
async def delete_product(
    product_id: uuid.UUID,
    current_user=Depends(require_permission(Entity.PRODUCTS, Action.DELETE)),
):
    """
    Eliminar producto - Solo SUPERADMIN puede eliminar productos.
    """
    return delete_product_service(product_id)
