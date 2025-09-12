from sqlalchemy.orm import Session
from database import engine
from models_db import Product
from schemas.product import ProductCreate, ProductUpdate, ProductResponse
from fastapi import HTTPException
import uuid

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
                category_id=product_data.category_id
            )
            session.add(db_product)
            session.commit()
            session.refresh(db_product)
            
            return {
                "message": "Product created successfully",
                "product": {
                    "id": str(db_product.id),
                    "name": db_product.name,
                    "description": db_product.description,
                    "category_id": str(db_product.category_id) if db_product.category_id else None
                }
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
                "category_id": str(product.category_id) if product.category_id else None
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
            "category_id": str(product.category_id) if product.category_id else None
        }

def update_product_service(product_id: uuid.UUID, product_data: ProductUpdate):
    """
    Servicio para actualizar un producto.
    """
    with Session(engine) as session:
        product = session.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Actualizar solo los campos que no son None
        if product_data.name is not None:
            product.name = product_data.name
        if product_data.description is not None:
            product.description = product_data.description
        if product_data.category_id is not None:
            product.category_id = product_data.category_id
        
        session.commit()
        session.refresh(product)
        
        return {
            "message": "Product updated successfully",
            "product": {
                "id": str(product.id),
                "name": product.name,
                "description": product.description,
                "category_id": str(product.category_id) if product.category_id else None
            }
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