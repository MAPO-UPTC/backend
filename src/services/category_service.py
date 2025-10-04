from contextlib import contextmanager
from typing import Dict, List, Optional, Any
from uuid import UUID

from database import engine
from models_db import Category
from schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


@contextmanager
def get_db_session():
    """Provide a transactional scope around a series of operations."""
    session = Session(engine)
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def _category_to_dict(category: Category) -> Dict[str, Optional[str]]:
    """Convert a Category model instance to a dictionary.
    
    Args:
        category: The Category model instance to convert.
        
    Returns:
        Dict containing the category's data.
    """
    return {
        "id": str(category.id),
        "name": category.name,
        "description": category.description,
    }

def _handle_db_error(error: Exception) -> Dict[str, str]:
    """Handle database errors and return appropriate error response.
    
    Args:
        error: The exception that was raised.
        
    Returns:
        Dict containing error information.
    """
    if isinstance(error, IntegrityError):
        return {
            "error": "database_error",
            "detail": "A category with this name already exists"
        }
    return {
        "error": "database_error",
        "detail": str(error.orig) if hasattr(error, "orig") else str(error)
    }

def create_category(category_data: CategoryCreate) -> Dict[str, Any]:
    """Create a new category.
    
    Args:
        category_data: Category data for creation.
        
    Returns:
        Dict containing the created category data or error information.
    """
    try:
        with get_db_session() as db:
            new_category = Category(
                name=category_data.name,
                description=category_data.description
            )
            db.add(new_category)
            db.commit()
            db.refresh(new_category)
            return _category_to_dict(new_category)
    except Exception as e:
        return _handle_db_error(e)

def get_categories() -> List[Dict[str, Any]]:
    """Retrieve all categories.
    
    Returns:
        List of category dictionaries.
    """
    with get_db_session() as db:
        categories = db.query(Category).all()
        return [_category_to_dict(category) for category in categories]

def get_category_by_id_service(category_id: UUID) -> Dict[str, Any]:
    """Retrieve a category by its ID.
    
    Args:
        category_id: The UUID of the category to retrieve.
        
    Returns:
        Dict containing the category data or error information.
    """
    with get_db_session() as db:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return {
                "error": "not_found",
                "detail": f"Category with id {category_id} not found"
            }
        return _category_to_dict(category)

def update_category_service(category_id: UUID, category_data: CategoryUpdate) -> Dict[str, Any]:
    """Update an existing category.
    
    Args:
        category_id: The UUID of the category to update.
        category_data: The updated category data.
        
    Returns:
        Dict containing the updated category data or error information.
    """
    try:
        with get_db_session() as db:
            category = db.query(Category).filter(Category.id == category_id).first()
            if not category:
                return {
                    "error": "not_found",
                    "detail": f"Category with id {category_id} not found"
                }

            update_data = category_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(category, key, value)

            db.commit()
            db.refresh(category)
            return _category_to_dict(category)
    except Exception as e:
        db.rollback()
        return _handle_db_error(e)

def delete_category_service(category_id: UUID) -> Dict[str, Any]:
    """Delete a category by its ID.
    
    Args:
        category_id: The UUID of the category to delete.
        
    Returns:
        Dict containing a success message or error information.
    """
    try:
        with get_db_session() as db:
            category = db.query(Category).filter(Category.id == category_id).first()
            if not category:
                return {
                    "error": "not_found",
                    "detail": f"Category with id {category_id} not found"
                }
            db.delete(category)
            db.commit()
            return {
                "message": "Category deleted successfully",
                "id": str(category_id)
            }
    except Exception as e:
        return _handle_db_error(e)
