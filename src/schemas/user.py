from pydantic import BaseModel
from typing import Optional
import uuid

from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid


class SignUpSchema(BaseModel):
    name: str
    last_name: str
    document_type: str
    document_number: str
    email: EmailStr
    password: str


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


# COMENTADO - Schema para Google login (no se usará por ahora)
# class GoogleLoginSchema(BaseModel):
#     token: str


class PersonResponse(BaseModel):
    id: uuid.UUID
    name: str
    last_name: str
    document_type: str
    document_number: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    uid: str
    person: PersonResponse

    class Config:
        from_attributes = True


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    document_type: Optional[str] = None
    document_number: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[str] = None
    person: Optional[PersonUpdate] = None


class LoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "string123",
            }
        }


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str
    second_first_name: Optional[str] = None
    last_name: str
    second_last_name: Optional[str] = None
    phone_code: Optional[str] = None
    phone_number: Optional[str] = None
    uid: Optional[str] = None
    role: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    second_first_name: Optional[str] = None
    last_name: Optional[str] = None
    second_last_name: Optional[str] = None
    phone_code: Optional[str] = None
    phone_number: Optional[str] = None


# Esquemas para manejo de roles activos
class SwitchRoleSchema(BaseModel):
    role: str  # Nombre del rol (USER, ADMIN, SUPERADMIN)


class ActiveRoleResponse(BaseModel):
    active_role: Optional[str] = None
    available_roles: list[str]
    permissions: dict


# Comentado - Login con Google (no se usará por ahora)
# class GoogleLoginRequest(BaseModel):
#     token: str
