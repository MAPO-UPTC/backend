from fastapi import APIRouter, Depends, Body
from models_db import BulkConversion
from sqlalchemy.orm import Session
from sqlalchemy import text
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


@router.post("/migrate-db/", response_model=dict)
async def migrate_product_presentation_table(
    current_user=Depends(require_permission(Entity.PRODUCTS, Action.CREATE)),
):
    """
    Migrar tabla product_presentation para agregar columnas faltantes.
    Solo ADMIN y SUPERADMIN pueden ejecutar esto.
    """
    migration_queries = [
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'product_presentation'
                AND column_name = 'price'
            ) THEN
                ALTER TABLE product_presentation ADD COLUMN price FLOAT NOT NULL DEFAULT 0.0;
            END IF;
        END $$;
        """,
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'product_presentation'
                AND column_name = 'sku'
            ) THEN
                ALTER TABLE product_presentation ADD COLUMN sku VARCHAR;
            END IF;
        END $$;
        """,
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'product_presentation'
                AND column_name = 'active'
            ) THEN
                ALTER TABLE product_presentation ADD COLUMN active INTEGER NOT NULL DEFAULT 1;
            END IF;
        END $$;
        """,
    ]

    try:
        with engine.connect() as connection:
            for query in migration_queries:
                connection.execute(text(query))
            connection.commit()
        return {"message": "Migration completed successfully", "status": "success"}
    except Exception as e:
        return {"message": f"Migration failed: {str(e)}", "status": "error"}


@router.post("/migrate-inventory-sales/", response_model=dict)
async def migrate_inventory_sales_tables(
    current_user=Depends(require_permission(Entity.PRODUCTS, Action.CREATE)),
):
    """
    Migrar tablas de inventario y ventas.
    Solo ADMIN y SUPERADMIN pueden ejecutar esto.
    """
    migration_queries = [
        # Crear tabla lot
        """
        CREATE TABLE IF NOT EXISTS lot (
            id TEXT PRIMARY KEY,
            supplier_name TEXT NOT NULL,
            purchase_date TIMESTAMP NOT NULL,
            invoice_number TEXT,
            total_cost REAL NOT NULL,
            notes TEXT
        )
        """,
        # Crear nueva tabla lot_detail con campos adicionales
        """
        CREATE TABLE IF NOT EXISTS lot_detail_new (
            id TEXT PRIMARY KEY,
            lot_id TEXT NOT NULL,
            presentation_id INTEGER NOT NULL,
            quantity_received INTEGER NOT NULL,
            quantity_available INTEGER NOT NULL,
            unit_cost REAL NOT NULL,
            batch_number TEXT,
            expiry_date TIMESTAMP,
            supplier_info TEXT
        )
        """,
        # Crear tabla sale
        """
        CREATE TABLE IF NOT EXISTS sale (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_code TEXT NOT NULL UNIQUE,
            sale_date TIMESTAMP NOT NULL,
            customer_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            total REAL NOT NULL,
            notes TEXT
        )
        """,
        # Crear tabla sale_detail
        """
        CREATE TABLE IF NOT EXISTS sale_detail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            presentation_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            discount REAL DEFAULT 0,
            subtotal REAL NOT NULL
        )
        """,
    ]

    try:
        with engine.connect() as connection:
            with connection.begin():
                for query in migration_queries:
                    connection.execute(text(query))

                # Migrar datos existentes de lot_detail si existe
                try:
                    connection.execute(
                        text(
                            """
                        INSERT INTO lot_detail_new (id, lot_id, presentation_id, quantity_received, quantity_available, unit_cost, batch_number)
                        SELECT id, lot_id, presentation_id, quantity_received, quantity_available, unit_cost, batch_number
                        FROM lot_detail
                    """
                        )
                    )

                    # Eliminar tabla vieja y renombrar
                    connection.execute(text("DROP TABLE lot_detail"))
                    connection.execute(
                        text("ALTER TABLE lot_detail_new RENAME TO lot_detail")
                    )
                except Exception:
                    # Si no existe la tabla vieja, solo renombrar
                    connection.execute(
                        text("ALTER TABLE lot_detail_new RENAME TO lot_detail")
                    )

        return {
            "message": "Inventory and sales tables migration completed successfully",
            "status": "success",
        }
    except Exception as e:
        return {
            "message": f"Inventory and sales migration failed: {str(e)}",
            "status": "error",
        }


@router.get("/bulk-stock/", response_model=list)
async def get_bulk_stock():
    """
    Consultar stock a granel activo (BulkConversion).
    """
    with Session(engine) as session:
        bulks = (
            session.query(BulkConversion)
            .filter(BulkConversion.status == "ACTIVE")
            .all()
        )
        return [
            {
                "bulk_conversion_id": str(bulk.id),
                "remaining_bulk": bulk.remaining_bulk,
                "converted_quantity": bulk.converted_quantity,
                "target_presentation_id": str(bulk.target_presentation_id),
                "conversion_date": str(bulk.conversion_date),
                "status": bulk.status,
            }
            for bulk in bulks
        ]


@router.post("/sell-bulk/", response_model=dict)
async def sell_bulk(
    bulk_conversion_id: uuid.UUID = Body(...),
    quantity: int = Body(...),
    unit_price: float = Body(...),
    customer_id: uuid.UUID = Body(...),
    user_id: uuid.UUID = Body(...),
    current_user=Depends(require_permission(Entity.PRODUCTS, Action.UPDATE)),
):
    """
    Registrar venta a granel y descontar stock.
    """
    return sell_bulk_service(
        bulk_conversion_id, quantity, unit_price, customer_id, user_id
    )


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
