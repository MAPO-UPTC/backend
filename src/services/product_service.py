from models_db import Sale, SaleDetail
from models_db import BulkConversion
from sqlalchemy import select

def sell_bulk_service(bulk_conversion_id: int, quantity: float, unit_price: float, customer_id: int, user_id: int):
    """
    Registrar venta a granel, descontar stock de BulkConversion y registrar movimiento/venta.
    """
    with Session(engine) as session:
        bulk = session.get(BulkConversion, bulk_conversion_id)
        if not bulk or bulk.status != "ACTIVE":
            raise HTTPException(status_code=404, detail="BulkConversion not found or inactive")
        if bulk.remaining_bulk < quantity:
            raise HTTPException(status_code=400, detail="No hay suficiente stock a granel disponible")
        # Descontar cantidad vendida
        bulk.remaining_bulk -= quantity
        if bulk.remaining_bulk <= 0:
            bulk.status = "DEPLETED"
        session.add(bulk)
        # Registrar venta y detalle
        sale = Sale(
            sale_code="BULK-" + str(bulk_conversion_id),
            sale_date=datetime.now(),
            customer_id=customer_id,
            user_id=user_id,
            total=quantity * unit_price,
            status="COMPLETED"
        )
        session.add(sale)
        session.commit()
        session.refresh(sale)
        sale_detail = SaleDetail(
            sale_id=sale.id,
            presentation_id=bulk.target_presentation_id,
            bulk_conversion_id=bulk.id,
            quantity=quantity,
            unit_price=unit_price,
            line_total=quantity * unit_price
        )
        session.add(sale_detail)
        session.commit()
        return {
            "sale_id": sale.id,
            "bulk_conversion_id": bulk.id,
            "remaining_bulk": bulk.remaining_bulk
        }
from models_db import BulkConversion, LotDetail
from schemas.product import BulkConversionCreate
from sqlalchemy import select
from datetime import datetime

def open_bulk_conversion_service(data: BulkConversionCreate):
    """
    Servicio para abrir un bulto y habilitar venta a granel.
    """
    with Session(engine) as session:
        # Buscar el detalle de lote
        lot_detail = session.execute(
            select(LotDetail).where(LotDetail.id == data.source_lot_detail_id)
        ).scalar_one_or_none()
        if not lot_detail:
            raise HTTPException(status_code=404, detail="LotDetail not found")
        # Validar que hay bultos disponibles
        if lot_detail.quantity_available < 1:
            raise HTTPException(status_code=400, detail="No hay bultos disponibles para abrir")
        # Restar 1 bulto
        lot_detail.quantity_available -= 1
        session.add(lot_detail)
        # Crear conversión a granel
        bulk = BulkConversion(
            source_lot_detail_id=data.source_lot_detail_id,
            target_presentation_id=data.target_presentation_id,
            converted_quantity=data.quantity,
            remaining_bulk=data.quantity,
            conversion_date=datetime.now(),
            status="ACTIVE"
        )
        session.add(bulk)
        session.commit()
        session.refresh(bulk)
        return {
            "bulk_conversion_id": bulk.id,
            "remaining_bulk": bulk.remaining_bulk
        }
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from database import engine
from models_db import Product, ProductPresentation
from schemas.product import ProductCreate, ProductUpdate


def create_product_service(product_data: ProductCreate):
    """
    Servicio para crear un producto.
    """
    try:
        print(f"Creating product: {product_data}")
        with Session(engine) as session:
            db_product = Product(
                name=product_data.name,
                description=product_data.description,
                brand=product_data.brand,
                base_unit=product_data.base_unit,
                category_id=product_data.category_id,
                image_url=product_data.image_url,
            )
            session.add(db_product)
            session.commit()
            session.refresh(db_product)

            # Registrar presentaciones asociadas
            for pres in getattr(product_data, "presentations", []):
                db_pres = ProductPresentation(
                    product_id=db_product.id,
                    presentation_name=pres.presentation_name,
                    quantity=pres.quantity,
                    unit=pres.unit,
                    price=pres.price,
                    sku=pres.sku,
                    active=pres.active
                )
                session.add(db_pres)
            session.commit()

            return {
                "message": "Product created successfully",
                "product": {
                    "id": str(db_product.id),
                    "name": db_product.name,
                    "description": db_product.description,
                    "brand": db_product.brand,
                    "base_unit": db_product.base_unit,
                    "category_id": (
                        str(db_product.category_id) if db_product.category_id else None
                    ),
                    "image_url": db_product.image_url,
                },
            }
    except Exception as e:
        print("Error creating product:", e)
        raise HTTPException(status_code=400, detail=f"Error creating product: {str(e)}")


def get_products_service():
    """
    Servicio para obtener todos los productos.
    """
    with Session(engine) as session:
        products = session.query(Product).all()
        return [
            {
                "id": str(product.id),
                "name": product.name,
                "description": product.description,
                "brand": product.brand,
                "base_unit": product.base_unit,
                "category_id": (
                    str(product.category_id) if product.category_id else None
                ),
                "image_url": product.image_url,
            }
            for product in products
        ]


def get_product_by_id_service(product_id: uuid.UUID):
    """
    Servicio para obtener un producto por ID.
    """
    with Session(engine) as session:
        product = session.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return {
            "id": str(product.id),
            "name": product.name,
            "description": product.description,
            "brand": product.brand,
            "base_unit": product.base_unit,
            "category_id": (str(product.category_id) if product.category_id else None),
            "image_url": product.image_url,
        }


def update_product_service(product_id: uuid.UUID, product_data: ProductUpdate):
    """
    Servicio para actualizar un producto.
    """
    with Session(engine) as session:
        product = session.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Actualizar solo los campos que fueron enviados explícitamente
        update_data = product_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(product, field):
                setattr(product, field, value)

        session.commit()
        session.refresh(product)

        return {
            "message": "Product updated successfully",
            "product": {
                "id": str(product.id),
                "name": product.name,
                "description": product.description,
                "brand": product.brand,
                "base_unit": product.base_unit,
                "category_id": (
                    str(product.category_id) if product.category_id else None
                ),
                "image_url": product.image_url,
            },
        }


def delete_product_service(product_id: uuid.UUID):
    """
    Servicio para eliminar un producto.
    """
    with Session(engine) as session:
        product = session.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        session.delete(product)
        session.commit()

        return {"message": "Product deleted successfully"}
