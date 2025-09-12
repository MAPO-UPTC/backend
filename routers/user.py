from fastapi import APIRouter, Depends, HTTPException
from schemas.user import SignUpSchema, LoginSchema, UserResponse, UserUpdate
from services.user_service import (
    create_user_service, 
    get_users_service, 
    get_user_by_id_service,
    update_user_service,
    login_service
)
from utils.auth import get_current_user
from typing import List
import uuid

router = APIRouter()

@router.post("/signup", response_model=dict)
async def create_user(user_data: SignUpSchema):
    """
    Crear una nueva cuenta de usuario con email y contraseña.
    """
    return create_user_service(user_data)

@router.post("/login")
async def login(user_data: LoginSchema):
    """
    Iniciar sesión con email y contraseña.
    """
    return login_service(user_data.email, user_data.password)

@router.get("/", response_model=List[UserResponse])
async def get_users(current_user=Depends(get_current_user)):
    """
    Obtener todos los usuarios (requiere autenticación).
    """
    return get_users_service()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: uuid.UUID, current_user=Depends(get_current_user)):
    """
    Obtener un usuario por ID (requiere autenticación).
    """
    return get_user_by_id_service(str(user_id))

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID, 
    user_data: UserUpdate,
    current_user=Depends(get_current_user)
):
    """
    Actualizar un usuario (requiere autenticación).
    """
    update_data = user_data.dict(exclude_unset=True)
    return update_user_service(str(user_id), update_data)

@router.post("/ping")
async def validate_token(current_user=Depends(get_current_user)):
    """
    Validar token y obtener información del usuario actual.
    """
    return {"message": "Token is valid", "user": current_user}

# COMENTADO - Login con Google (no se usará por ahora)
# @router.post("/auth/google")
# async def google_login(request: GoogleLoginRequest):
#     """
#     Iniciar sesión con Google usando Firebase token.
#     """
#     return google_login_service(request.token)