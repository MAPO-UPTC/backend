"""
Servicio para manejo de proveedores
"""

from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models_db import Supplier
from schemas.supplier import SupplierCreate, SupplierUpdate


def create_supplier(db: Session, supplier: SupplierCreate) -> Supplier:
    """
    Crear un nuevo proveedor
    """
    db_supplier = Supplier(
        name=supplier.name,
        address=supplier.address,
        phone_number=supplier.phone_number,
        email=supplier.email,
        contact_person=supplier.contact_person,
    )
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


def get_suppliers(db: Session, skip: int = 0, limit: int = 100) -> List[Supplier]:
    """
    Obtener lista de proveedores con paginación
    """
    return db.query(Supplier).offset(skip).limit(limit).all()


def get_supplier_by_id(db: Session, supplier_id: str) -> Optional[Supplier]:
    """
    Obtener un proveedor por su ID
    """
    return db.query(Supplier).filter(Supplier.id == supplier_id).first()


def update_supplier(
    db: Session, supplier_id: str, supplier_data: SupplierUpdate
) -> Supplier:
    """
    Actualizar un proveedor existente
    """
    supplier = get_supplier_by_id(db, supplier_id)
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    # Actualizar solo los campos que fueron enviados explícitamente
    update_data = supplier_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(supplier, field):
            setattr(supplier, field, value)
    
    db.commit()
    db.refresh(supplier)
    
    return supplier


def delete_supplier(db: Session, supplier_id: str) -> dict:
    """
    Eliminar un proveedor
    """
    supplier = get_supplier_by_id(db, supplier_id)
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    db.delete(supplier)
    db.commit()
    
    return {"message": "Proveedor eliminado exitosamente"}
