
from fastapi import APIRouter, Depends, Body
from models_db import BulkConversion
from sqlalchemy.orm import Session
from database import engine
from config.permissions import Action, Entity
from schemas.product import ProductCreate, ProductUpdate, BulkConversionCreate
from services.product_service import (
    create_product_service,
    delete_product_service,
    get_product_by_id_service,
    get_products_service,
    update_product_service,
    sell_bulk_service,
    open_bulk_conversion_service,
)
from utils.auth import require_permission
import uuid
from typing import List

router = APIRouter()

@router.get("/bulk-stock/", response_model=list)
async def get_bulk_stock():
    """
    Consultar stock a granel activo (BulkConversion).
    """
    with Session(engine) as session:
        bulks = session.query(BulkConversion).filter(BulkConversion.status == "ACTIVE").all()
        return [
            {
                "bulk_conversion_id": bulk.id,
                "remaining_bulk": bulk.remaining_bulk,
                "converted_quantity": bulk.converted_quantity,
                "target_presentation_id": bulk.target_presentation_id,
                "conversion_date": str(bulk.conversion_date),
                "status": bulk.status
            }
            for bulk in bulks
        ]
@router.post("/sell-bulk/", response_model=dict)
async def sell_bulk(
    bulk_conversion_id: int = Body(...),
    quantity: float = Body(...),
    unit_price: float = Body(...),
    customer_id: int = Body(...),
    user_id: int = Body(...),
    current_user=Depends(require_permission(Entity.PRODUCTS, Action.UPDATE)),
):
    """
    Registrar venta a granel y descontar stock.
    """
    return sell_bulk_service(bulk_conversion_id, quantity, unit_price, customer_id, user_id)

@router.post("/open-bulk/", response_model=dict)
async def open_bulk(
    data: BulkConversionCreate,
    current_user=Depends(require_permission(Entity.PRODUCTS, Action.UPDATE)),
):
    """
    Abrir bulto y habilitar venta a granel.
    """
    return open_bulk_conversion_service(data)


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
