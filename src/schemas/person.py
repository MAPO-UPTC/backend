import uuid
from typing import Optional

from pydantic import BaseModel, Field


class PersonCreate(BaseModel):
    """
    Schema para crear una nueva persona/cliente.
    """

    name: str = Field(
        ..., min_length=1, max_length=100, description="Nombre de la persona"
    )
    last_name: str = Field(
        ..., min_length=1, max_length=100, description="Apellido de la persona"
    )
    document_type: str = Field(
        ..., description="Tipo de documento (CC, CE, NIT, PP, etc.)"
    )
    document_number: str = Field(
        ..., min_length=1, max_length=20, description="Número de documento"
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "Juan Carlos",
                "last_name": "Pérez García",
                "document_type": "CC",
                "document_number": "12345678",
            }
        }


class PersonResponse(BaseModel):
    """
    Esquema de respuesta para una persona.
    """

    id: uuid.UUID
    name: str
    last_name: str
    document_type: str
    document_number: str
    full_name: str = Field(..., description="Nombre completo calculado")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "67825f4c-e43f-4871-8b46-6016ceebbecf",
                "name": "Juan Carlos",
                "last_name": "Pérez García",
                "document_type": "CC",
                "document_number": "12345678",
                "full_name": "Juan Carlos Pérez García",
            }
        }


class PersonUpdate(BaseModel):
    """
    Schema para actualizar una persona.
    """

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    document_type: Optional[str] = None
    document_number: Optional[str] = Field(None, min_length=1, max_length=20)

    class Config:
        schema_extra = {"example": {"name": "Juan Carlos", "document_type": "CE"}}
