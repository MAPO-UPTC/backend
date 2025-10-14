import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from schemas.person import PersonCreate, PersonResponse, PersonUpdate
from services.person_service import (
    create_person_service,
    get_all_persons_service,
    get_person_by_id_service,
    search_persons_service,
    update_person_service,
)
from utils.auth import get_current_user_from_db

router = APIRouter()


@router.post("/", status_code=201, response_model=PersonResponse)
async def create_person(person_data: PersonCreate):
    """
    Crear una nueva persona/cliente sin necesidad de cuenta de usuario.
    No requiere autenticación - endpoint público para registro rápido de clientes.

    Validaciones automáticas:
    - Documento único (tipo + número)
    - Campos requeridos: name, last_name, document_type, document_number
    """
    return create_person_service(person_data)


@router.get("/", response_model=List[PersonResponse])
async def get_all_persons(
    search: Optional[str] = Query(
        None, description="Buscar por nombre, apellido o documento"
    ),
    current_user=Depends(get_current_user_from_db),
):
    """
    Obtener todas las personas registradas en el sistema.
    Incluye funcionalidad de búsqueda opcional.
    Requiere autenticación.
    """
    if search:
        return search_persons_service(search)
    return get_all_persons_service()


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person_by_id(
    person_id: uuid.UUID, current_user=Depends(get_current_user_from_db)
):
    """
    Obtener una persona específica por ID.
    Requiere autenticación.
    """
    return get_person_by_id_service(person_id)


@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(
    person_id: uuid.UUID,
    person_data: PersonUpdate,
    current_user=Depends(get_current_user_from_db),
):
    """
    Actualizar información de una persona existente.
    Requiere autenticación.

    Validaciones:
    - Documento único (si se cambia)
    - Solo actualiza campos proporcionados
    """
    return update_person_service(person_id, person_data)
