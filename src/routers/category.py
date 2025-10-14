import uuid
from typing import List

from fastapi import APIRouter, Depends

from config.permissions import Action, Entity
from schemas.category import CategoryCreate, CategoryUpdate
from services.category_service import (
    create_category_service,
    create_petshop_default_categories,
    delete_category_service,
    get_categories_service,
    get_category_by_id_service,
    update_category_service,
)
from utils.auth import require_permission

router = APIRouter()


@router.post("/setup-petshop-defaults/", response_model=dict)
async def setup_petshop_default_categories(
    current_user=Depends(require_permission(Entity.PRODUCTS, Action.CREATE)),
):
    """
    Crear categorías por defecto para petshop (solo ejecutar una vez).
    Solo ADMIN y SUPERADMIN pueden ejecutar esto.
    """
    return create_petshop_default_categories()


@router.post("/", response_model=dict)
async def create_category(
    category_data: CategoryCreate,
    current_user=Depends(require_permission(Entity.PRODUCTS, Action.CREATE)),
):
    """
    Crear nueva categoría - Solo ADMIN y SUPERADMIN pueden crear categorías.
    """
    return create_category_service(category_data)


@router.get("/", response_model=List[dict])
async def get_categories():
    """
    Obtener todas las categorías activas (público).
    """
    return get_categories_service()


@router.get("/{category_id}", response_model=dict)
async def get_category(category_id: uuid.UUID):
    """
    Obtener una categoría por ID (público).
    """
    return get_category_by_id_service(category_id)


@router.put("/{category_id}", response_model=dict)
async def update_category(
    category_id: uuid.UUID,
    category_data: CategoryUpdate,
    current_user=Depends(require_permission(Entity.PRODUCTS, Action.UPDATE)),
):
    """
    Actualizar categoría - Solo ADMIN y SUPERADMIN pueden actualizar categorías.
    """
    return update_category_service(category_id, category_data)


@router.get("/{category_id}/products", response_model=List[dict])
async def get_products_by_category(category_id: uuid.UUID):
    """
    Obtener todos los productos de una categoría específica (público).
    """
    from services.product_service import get_products_by_category_service

    return get_products_by_category_service(category_id)


@router.delete("/{category_id}")
async def delete_category(
    category_id: uuid.UUID,
    current_user=Depends(require_permission(Entity.PRODUCTS, Action.DELETE)),
):
    """
    Eliminar categoría - Solo SUPERADMIN puede eliminar categorías.
    """
    return delete_category_service(category_id)
