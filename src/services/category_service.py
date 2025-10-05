import uuid
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from database import engine
from models_db import Category
from schemas.category import CategoryCreate, CategoryUpdate


def create_category_service(category_data: CategoryCreate):
    """
    Servicio para crear una categoría.
    """
    try:
        with Session(engine) as session:
            db_category = Category(
                name=category_data.name,
                description=category_data.description,
                active=category_data.active,
            )
            session.add(db_category)
            session.commit()
            session.refresh(db_category)

            return {
                "message": "Category created successfully",
                "category": {
                    "id": str(db_category.id),
                    "name": db_category.name,
                    "description": db_category.description,
                    "active": db_category.active,
                },
            }
    except Exception as e:
        print("Error creating category:", e)
        raise HTTPException(status_code=400, detail=f"Error creating category: {str(e)}")


def get_categories_service():
    """
    Servicio para obtener todas las categorías activas.
    """
    with Session(engine) as session:
        categories = session.query(Category).filter(Category.active == True).all()
        return [
            {
                "id": str(category.id),
                "name": category.name,
                "description": category.description,
                "active": category.active,
            }
            for category in categories
        ]


def get_category_by_id_service(category_id: uuid.UUID):
    """
    Servicio para obtener una categoría por ID.
    """
    with Session(engine) as session:
        category = session.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return {
            "id": str(category.id),
            "name": category.name,
            "description": category.description,
            "active": category.active,
        }


def update_category_service(category_id: uuid.UUID, category_data: CategoryUpdate):
    """
    Servicio para actualizar una categoría.
    """
    with Session(engine) as session:
        category = session.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        if category_data.name is not None:
            category.name = category_data.name
        if category_data.description is not None:
            category.description = category_data.description
        if category_data.active is not None:
            category.active = category_data.active

        session.commit()
        session.refresh(category)
        return {
            "message": "Category updated successfully",
            "category": {
                "id": str(category.id),
                "name": category.name,
                "description": category.description,
                "active": category.active,
            },
        }


def delete_category_service(category_id: uuid.UUID):
    """
    Servicio para eliminar (desactivar) una categoría.
    """
    with Session(engine) as session:
        category = session.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        category.active = False
        session.commit()
        return {"message": "Category deleted successfully"}


def create_petshop_default_categories():
    """
    Crear categorías por defecto para un petshop.
    """
    default_categories = [
        {
            "name": "Alimento para Perros",
            "description": "Concentrados, snacks y alimentos específicos para perros de todas las edades"
        },
        {
            "name": "Alimento para Gatos", 
            "description": "Concentrados, snacks y alimentos específicos para gatos"
        },
        {
            "name": "Alimento para Aves",
            "description": "Semillas, concentrados y suplementos para aves domésticas"
        },
        {
            "name": "Alimento para Peces",
            "description": "Alimentos específicos para peces de acuario y ornamentales"
        },
        {
            "name": "Alimento para Roedores",
            "description": "Alimentos para hamsters, conejos, cobayas y otros roedores"
        },
        {
            "name": "Higiene y Cuidado",
            "description": "Shampoos, acondicionadores, productos de aseo y cuidado personal"
        },
        {
            "name": "Medicamentos y Suplementos",
            "description": "Vitaminas, suplementos nutricionales y productos veterinarios"
        },
        {
            "name": "Juguetes y Entretenimiento",
            "description": "Juguetes, pelotas, cuerdas y accesorios de entretenimiento"
        },
        {
            "name": "Accesorios y Correas",
            "description": "Collares, correas, arneses y accesorios para paseo"
        },
        {
            "name": "Camas y Descanso",
            "description": "Camas, cojines, mantas y accesorios para el descanso"
        },
        {
            "name": "Transportadoras y Jaulas",
            "description": "Transportadoras, jaulas, terrarios y habitáculos"
        },
        {
            "name": "Arena y Aseo",
            "description": "Arena para gatos, productos de limpieza y aseo del hogar"
        }
    ]
    
    try:
        with Session(engine) as session:
            created_categories = []
            for cat_data in default_categories:
                # Verificar si ya existe
                existing = session.query(Category).filter(Category.name == cat_data["name"]).first()
                if not existing:
                    db_category = Category(
                        name=cat_data["name"],
                        description=cat_data["description"],
                        active=True
                    )
                    session.add(db_category)
                    created_categories.append(cat_data["name"])
            
            session.commit()
            return {
                "message": f"Created {len(created_categories)} default petshop categories",
                "categories": created_categories
            }
    except Exception as e:
        print("Error creating default categories:", e)
        raise HTTPException(status_code=400, detail=f"Error creating categories: {str(e)}")