import uuid
from typing import Optional

from pydantic import BaseModel


class SupplierCreate(BaseModel):
    """Schema para crear un proveedor"""

    name: str
    address: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    contact_person: Optional[str] = None


class SupplierUpdate(BaseModel):
    """Schema para actualizar un proveedor"""

    name: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    contact_person: Optional[str] = None


class SupplierResponse(BaseModel):
    """Schema para respuesta de proveedor"""

    id: uuid.UUID
    name: str
    address: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    contact_person: Optional[str] = None

    class Config:
        from_attributes = True
