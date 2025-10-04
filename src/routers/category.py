from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import CategorySchema, CategoryUpdateSchema
from src.models_db import Category
from src.services import category_service

router = APIRouter()

@router.post("/", response_model=dict)
def create_category(category: CategorySchema):
    return category_service.create_category(category)

@router.get("/", response_model=list)
def list_categories():
    return category_service.get_categories()

@router.get("/with-products")
def list_categories_with_products():
    return category_service.get_categories(include_products=True)

@router.get("/{category_id}", response_model=dict)
def get_category(category_id: UUID):
    category = category_service.get_category_by_id_service(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/{category_id}", response_model=dict)
def update_category(category_id: UUID, category: CategoryUpdateSchema):
    updated = category_service.update_category_service(category_id, category)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated

@router.delete("/{category_id}", response_model=dict)
def delete_category(category_id: UUID):
    deleted = category_service.delete_category_service(category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}

@router.get("/{category_id}/products")
def get_category_with_products(category_id: UUID, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return {"error": "Category not found"}
    return {"category": category.name, "products": category.products}