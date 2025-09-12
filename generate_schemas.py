#!/usr/bin/env python3
"""
Script para generar esquemas Pydantic automáticamente desde modelos SQLAlchemy.
"""

import inspect
from typing import get_type_hints, Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from models_db import Base
import uuid


def sqlalchemy_to_pydantic_type(column):
    """Convierte tipos SQLAlchemy a tipos Python/Pydantic."""
    if isinstance(column.type, Integer):
        return "int"
    elif isinstance(column.type, String):
        return "str"
    elif isinstance(column.type, Text):
        return "str"
    elif isinstance(column.type, Boolean):
        return "bool"
    elif isinstance(column.type, DateTime):
        return "datetime"
    elif isinstance(column.type, Numeric):
        return "Decimal"
    elif isinstance(column.type, UUID):
        return "uuid.UUID"
    else:
        return "str"  # Default fallback


def generate_pydantic_schema(model_class):
    """Genera un esquema Pydantic desde un modelo SQLAlchemy."""
    class_name = model_class.__name__
    
    # Schema para crear (sin ID)
    create_schema = f"""
class {class_name}Create(BaseModel):"""
    
    # Schema para respuesta (con ID)
    response_schema = f"""
class {class_name}Response(BaseModel):"""
    
    # Schema para actualizar (todos opcionales)
    update_schema = f"""
class {class_name}Update(BaseModel):"""
    
    imports = set()
    imports.add("from pydantic import BaseModel")
    imports.add("from typing import Optional")
    
    for column in model_class.__table__.columns:
        col_name = column.name
        col_type = sqlalchemy_to_pydantic_type(column)
        is_nullable = column.nullable
        is_primary_key = column.primary_key
        
        # Agregar imports necesarios
        if col_type == "datetime":
            imports.add("from datetime import datetime")
        elif col_type == "Decimal":
            imports.add("from decimal import Decimal")
        elif col_type == "uuid.UUID":
            imports.add("import uuid")
        
        # Para Create schema (sin primary keys)
        if not is_primary_key:
            if is_nullable:
                create_schema += f"\n    {col_name}: Optional[{col_type}] = None"
            else:
                create_schema += f"\n    {col_name}: {col_type}"
        
        # Para Response schema (con todo)
        if is_nullable and not is_primary_key:
            response_schema += f"\n    {col_name}: Optional[{col_type}] = None"
        else:
            response_schema += f"\n    {col_name}: {col_type}"
        
        # Para Update schema (todo opcional)
        update_schema += f"\n    {col_name}: Optional[{col_type}] = None"
    
    # Agregar configuración
    config = """
    
    class Config:
        from_attributes = True"""
    
    response_schema += config
    
    return imports, create_schema, response_schema, update_schema


def generate_all_schemas():
    """Genera esquemas para todos los modelos."""
    output = """# Esquemas generados automáticamente
# Este archivo fue generado por generate_schemas.py

"""
    
    all_imports = set()
    all_schemas = []
    
    # Obtener todas las clases que heredan de Base
    for name, obj in inspect.getmembers(Base.registry._class_registry):
        if inspect.isclass(obj) and hasattr(obj, '__table__'):
            imports, create, response, update = generate_pydantic_schema(obj)
            all_imports.update(imports)
            all_schemas.extend([create, response, update])
    
    # Agregar imports
    for imp in sorted(all_imports):
        output += imp + "\n"
    
    output += "\n"
    
    # Agregar esquemas
    for schema in all_schemas:
        output += schema + "\n\n"
    
    return output


if __name__ == "__main__":
    schema_content = generate_all_schemas()
    
    # Guardar en archivo
    with open("schemas/generated_schemas.py", "w", encoding="utf-8") as f:
        f.write(schema_content)
    
    print("✅ Esquemas generados en schemas/generated_schemas.py")
    print("\nPara usar los esquemas:")
    print("from schemas.generated_schemas import UserCreate, UserResponse, UserUpdate")