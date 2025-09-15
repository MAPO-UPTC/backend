from fastapi import APIRouter, Depends, HTTPException
from schemas.user import (
    SignUpSchema,
    LoginSchema,
    UserResponse,
    UserUpdate,
    SwitchRoleSchema,
    ActiveRoleResponse,
)
from services.user_service import (
    create_user_service,
    get_users_service,
    get_user_by_id_service,
    update_user_service,
    login_service,
)
from utils.auth import (
    get_current_user,
    get_current_user_from_db,
    get_user_with_permissions,
    ActiveRoleManager,
)
from config.permissions import PermissionManager
from constants.role import RoleEnum
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
    current_user=Depends(get_current_user),
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


@router.get("/me/permissions")
async def get_my_permissions(user=Depends(get_user_with_permissions)):
    """
    Obtener todos los permisos del usuario actual para el frontend.
    Incluye información sobre rol activo y roles disponibles.
    """
    return {
        "user_id": str(user.id),
        "available_roles": [role.value for role in user.roles],
        "active_role": user.active_role.value if user.active_role else None,
        "effective_roles": [role.value for role in user.effective_roles],
        "permissions": user.permissions,
    }


@router.get("/me/profile")
async def get_my_profile(user=Depends(get_current_user_from_db)):
    """
    Obtener perfil completo del usuario actual.
    """
    return {
        "user": {"id": str(user.id), "email": user.email, "uid": user.uid},
        "person": {
            "id": str(user.person.id),
            "name": user.person.name,
            "last_name": user.person.last_name,
            "document_type": user.person.document_type,
            "document_number": user.person.document_number,
        },
        "roles": [role.value for role in user.roles],
    }


@router.post("/me/switch-role", response_model=ActiveRoleResponse)
async def switch_role(
    role_data: SwitchRoleSchema, user=Depends(get_current_user_from_db)
):
    """
    Cambiar el rol activo del usuario.
    El usuario solo puede cambiar a un rol que tenga asignado.
    """
    user_id = str(user.id)

    # Verificar que el rol solicitado existe
    try:
        requested_role = RoleEnum(role_data.role)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role: {role_data.role}. Valid roles: {[r.value for r in RoleEnum]}",
        )

    # Verificar que el usuario tiene este rol asignado
    if requested_role not in user.roles:
        available_roles = [role.value for role in user.roles]
        raise HTTPException(
            status_code=403,
            detail=f"User does not have role '{role_data.role}'. Available roles: {available_roles}",
        )

    # Establecer el rol activo
    ActiveRoleManager.set_active_role(user_id, requested_role)

    # Calcular permisos para el nuevo rol activo
    permissions = PermissionManager.get_user_permissions(requested_role)

    return ActiveRoleResponse(
        active_role=requested_role.value,
        available_roles=[role.value for role in user.roles],
        permissions=permissions,
    )


@router.post("/me/clear-active-role")
async def clear_active_role(user=Depends(get_current_user_from_db)):
    """
    Limpiar el rol activo del usuario.
    Después de esto, el usuario usará todos sus roles combinados.
    """
    user_id = str(user.id)
    ActiveRoleManager.clear_active_role(user_id)

    return {
        "message": "Active role cleared. Now using all assigned roles.",
        "available_roles": [role.value for role in user.roles],
    }


@router.get("/me/active-role", response_model=ActiveRoleResponse)
async def get_active_role(user=Depends(get_user_with_permissions)):
    """
    Obtener el rol activo actual del usuario.
    """
    return ActiveRoleResponse(
        active_role=user.active_role.value if user.active_role else None,
        available_roles=[role.value for role in user.roles],
        permissions=user.permissions,
    )


# COMENTADO - Login con Google (no se usará por ahora)
# @router.post("/auth/google")
# async def google_login(request: GoogleLoginRequest):
#     """
#     Iniciar sesión con Google usando Firebase token.
#     """
#     return google_login_service(request.token)
