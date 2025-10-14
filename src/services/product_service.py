import uuid
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database import engine
from models_db import Sale, SaleDetail, BulkConversion, LotDetail
from schemas.product import BulkConversionCreate
from sqlalchemy import select

def sell_bulk_service(bulk_conversion_id: uuid.UUID, quantity: int, unit_price: float, customer_id: uuid.UUID, user_id: uuid.UUID):
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
    
    Ejemplo: Si tienes 1 bulto de 25kg y quieres abrirlo:
    - converted_quantity = 1 (abres 1 bulto)
    - unit_conversion_factor = 25 (cada bulto contiene 25kg)
    - Resultado: Se crean 25kg a granel
    """
    with Session(engine) as session:
        # Buscar el detalle de lote
        lot_detail = session.execute(
            select(LotDetail).where(LotDetail.id == data.source_lot_detail_id)
        ).scalar_one_or_none()
        
        if not lot_detail:
            raise HTTPException(status_code=404, detail="LotDetail not found")
        
        # Validar que hay suficientes bultos disponibles
        if lot_detail.quantity_available < data.converted_quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"No hay suficientes bultos disponibles. Disponibles: {lot_detail.quantity_available}, Solicitados: {data.converted_quantity}"
            )
        
        # Calcular cantidad total a granel
        # Si abres 1 bulto de 25kg = 25kg
        # Si abres 2 bultos de 25kg = 50kg
        total_bulk_quantity = data.converted_quantity * data.unit_conversion_factor
        
        # Restar los bultos convertidos
        lot_detail.quantity_available -= data.converted_quantity
        session.add(lot_detail)
        
        # Crear conversión a granel
        bulk = BulkConversion(
            source_lot_detail_id=data.source_lot_detail_id,
            target_presentation_id=data.target_presentation_id,
            converted_quantity=data.converted_quantity,           # Cantidad de bultos abiertos
            remaining_bulk=total_bulk_quantity,                   # Cantidad total a granel disponible
            conversion_date=datetime.now(),
            status="ACTIVE"
        )
        session.add(bulk)
        session.commit()
        session.refresh(bulk)
        
        return {
            "message": f"Bulto(s) abierto(s) exitosamente. {total_bulk_quantity} unidades disponibles a granel",
            "bulk_conversion_id": str(bulk.id),
            "converted_quantity": bulk.converted_quantity,        # Bultos convertidos
            "remaining_bulk": bulk.remaining_bulk,                # Cantidad a granel disponible
            "total_bulk_created": total_bulk_quantity,            # Total creado a granel
            "unit_conversion_factor": data.unit_conversion_factor,
            "status": bulk.status
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
    Servicio para obtener todos los productos con información de stock disponible,
    incluyendo stock a granel (BulkConversion).
    """
    from sqlalchemy import func
    from models_db import ProductPresentation, LotDetail, BulkConversion
    
    with Session(engine) as session:
        products = session.query(Product).all()
        result = []
        
        for product in products:
            # Obtener presentaciones activas del producto
            presentations = session.query(ProductPresentation).filter(
                ProductPresentation.product_id == product.id,
                ProductPresentation.active == True
            ).all()
            
            # Calcular stock para cada presentación
            presentations_with_stock = []
            for presentation in presentations:
                # Calcular stock disponible en lotes normales
                stock_available = session.query(
                    func.coalesce(func.sum(LotDetail.quantity_available), 0)
                ).filter(
                    LotDetail.presentation_id == presentation.id
                ).scalar() or 0
                
                # Calcular stock a granel disponible para esta presentación
                bulk_stock = session.query(
                    func.coalesce(func.sum(BulkConversion.remaining_bulk), 0)
                ).filter(
                    BulkConversion.target_presentation_id == presentation.id,
                    BulkConversion.status == "ACTIVE"
                ).scalar() or 0
                
                presentations_with_stock.append({
                    "id": str(presentation.id),
                    "presentation_name": presentation.presentation_name,
                    "quantity": presentation.quantity,
                    "unit": presentation.unit,
                    "sku": presentation.sku,
                    "price": float(presentation.price),
                    "stock_available": int(stock_available),
                    "bulk_stock_available": int(bulk_stock),  # ✅ Nuevo campo
                    "total_stock": int(stock_available + bulk_stock),  # ✅ Stock total
                    "active": presentation.active
                })
            
            result.append({
                "id": str(product.id),
                "name": product.name,
                "description": product.description,
                "brand": product.brand,
                "base_unit": product.base_unit,
                "category_id": (
                    str(product.category_id) if product.category_id else None
                ),
                "image_url": product.image_url,
                "presentations": presentations_with_stock
            })
        
        return result


def get_product_by_id_service(product_id: uuid.UUID):
    """
    Servicio para obtener un producto por ID con información completa de presentaciones y stock.
    """
    from sqlalchemy import func
    from models_db import ProductPresentation, LotDetail, BulkConversion
    
    with Session(engine) as session:
        product = session.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Obtener presentaciones activas del producto
        presentations = session.query(ProductPresentation).filter(
            ProductPresentation.product_id == product.id,
            ProductPresentation.active == True
        ).all()
        
        # Calcular stock para cada presentación
        presentations_with_stock = []
        for presentation in presentations:
            # Calcular stock disponible en lotes normales
            stock_available = session.query(
                func.coalesce(func.sum(LotDetail.quantity_available), 0)
            ).filter(
                LotDetail.presentation_id == presentation.id
            ).scalar() or 0
            
            # Calcular stock a granel disponible para esta presentación
            bulk_stock = session.query(
                func.coalesce(func.sum(BulkConversion.remaining_bulk), 0)
            ).filter(
                BulkConversion.target_presentation_id == presentation.id,
                BulkConversion.status == "ACTIVE"
            ).scalar() or 0
            
            presentations_with_stock.append({
                "id": str(presentation.id),
                "presentation_name": presentation.presentation_name,
                "quantity": presentation.quantity,
                "unit": presentation.unit,
                "sku": presentation.sku,
                "price": float(presentation.price),
                "stock_available": int(stock_available),
                "bulk_stock_available": int(bulk_stock),  # ✅ Nuevo campo
                "total_stock": int(stock_available + bulk_stock),  # ✅ Stock total
                "active": presentation.active
            })

        return {
            "id": str(product.id),
            "name": product.name,
            "description": product.description,
            "brand": product.brand,
            "base_unit": product.base_unit,
            "category_id": (str(product.category_id) if product.category_id else None),
            "image_url": product.image_url,
            "presentations": presentations_with_stock  # ✅ Incluir presentaciones con stock
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


def get_products_by_category_service(category_id: uuid.UUID):
    """
    Servicio para obtener todos los productos de una categoría específica,
    incluyendo información de stock disponible y stock a granel.
    """
    from sqlalchemy import func
    from models_db import Product, ProductPresentation, LotDetail, BulkConversion
    
    with Session(engine) as session:
        # Filtrar productos por category_id
        products = session.query(Product).filter(
            Product.category_id == category_id
        ).all()
        
        result = []
        
        for product in products:
            # Obtener presentaciones activas del producto
            presentations = session.query(ProductPresentation).filter(
                ProductPresentation.product_id == product.id,
                ProductPresentation.active == True
            ).all()
            
            # Calcular stock para cada presentación
            presentations_with_stock = []
            for presentation in presentations:
                # Calcular stock disponible en lotes normales
                stock_available = session.query(
                    func.coalesce(func.sum(LotDetail.quantity_available), 0)
                ).filter(
                    LotDetail.presentation_id == presentation.id
                ).scalar() or 0
                
                # Calcular stock a granel disponible para esta presentación
                bulk_stock = session.query(
                    func.coalesce(func.sum(BulkConversion.remaining_bulk), 0)
                ).filter(
                    BulkConversion.target_presentation_id == presentation.id,
                    BulkConversion.status == "ACTIVE"
                ).scalar() or 0
                
                presentations_with_stock.append({
                    "id": str(presentation.id),
                    "presentation_name": presentation.presentation_name,
                    "quantity": presentation.quantity,
                    "unit": presentation.unit,
                    "sku": presentation.sku,
                    "price": float(presentation.price),
                    "stock_available": int(stock_available),
                    "bulk_stock_available": int(bulk_stock),
                    "total_stock": int(stock_available + bulk_stock),
                    "active": presentation.active
                })
            
            result.append({
                "id": str(product.id),
                "name": product.name,
                "description": product.description,
                "brand": product.brand,
                "base_unit": product.base_unit,
                "category_id": str(product.category_id) if product.category_id else None,
                "image_url": product.image_url,
                "presentations": presentations_with_stock
            })
        
        return result
