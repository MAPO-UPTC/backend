from sqlalchemy.orm import Session
from database import engine
from schemas.product import ProductCreate, ProductUpdate, ProductResponse
from fastapi import HTTPException
from typing import List, Optional
import uuid

# Nota: Necesitarás crear el modelo Product en models_db.py
# from models_db import Product

def create_product_service(product_data: ProductCreate):
    """
    Servicio para crear un producto.
    """
    with Session(engine) as session:
        db_product = Product(
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            stock=product_data.stock,
            category=product_data.category
        )
        session.add(db_product)
        session.commit()
        session.refresh(db_product)
        return db_product
    
    # Por ahora retorna un ejemplo
    return {"message": "Product created successfully (mock)"}

def get_products_service() -> List[dict]:
    """
    Servicio para obtener todos los productos.
    """
    # with Session(engine) as session:
    #     products = session.query(Product).all()
    #     return products
    
    # Por ahora retorna un ejemplo
    return [{"id": "123", "name": "Producto ejemplo", "price": 29.99}]

def get_product_by_id_service(product_id: uuid.UUID):
    """
    Servicio para obtener un producto por ID.
    """
    # with Session(engine) as session:
    #     product = session.query(Product).filter(Product.id == product_id).first()
    #     if not product:
    #         raise HTTPException(status_code=404, detail="Product not found")
    #     return product
    
    # Por ahora retorna un ejemplo
    return {"id": str(product_id), "name": "Producto ejemplo", "price": 29.99}

def update_product_service(product_id: uuid.UUID, product_data: ProductUpdate):
    """
    Servicio para actualizar un producto.
    """
    # with Session(engine) as session:
    #     product = session.query(Product).filter(Product.id == product_id).first()
    #     if not product:
    #         raise HTTPException(status_code=404, detail="Product not found")
    #     
    #     for field, value in product_data.dict(exclude_unset=True).items():
    #         setattr(product, field, value)
    #     
    #     session.commit()
    #     session.refresh(product)
    #     return product
    
    # Por ahora retorna un ejemplo
    return {"message": "Product updated successfully (mock)"}

def delete_product_service(product_id: uuid.UUID):
    """
    Servicio para eliminar un producto.
    """
    # with Session(engine) as session:
    #     product = session.query(Product).filter(Product.id == product_id).first()
    #     if not product:
    #         raise HTTPException(status_code=404, detail="Product not found")
    #     
    #     session.delete(product)
    #     session.commit()
    #     return {"message": "Product deleted successfully"}
    
    # Por ahora retorna un ejemplo
    return {"message": "Product deleted successfully (mock)"}