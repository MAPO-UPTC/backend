from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models_db import Person
from schemas.user import PersonResponse
from utils.auth import get_current_user_from_db

router = APIRouter()


@router.get("/", response_model=List[PersonResponse])
async def get_all_persons(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_from_db)
):
    """
    Obtener todas las personas registradas en el sistema.
    Requiere autenticación.
    """
    persons = db.query(Person).all()
    return persons


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person_by_id(
    person_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_from_db)
):
    """
    Obtener una persona específica por ID.
    Requiere autenticación.
    """
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person