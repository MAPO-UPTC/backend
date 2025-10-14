import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import engine
from models_db import Person
from schemas.person import PersonCreate, PersonUpdate


def create_person_service(person_data: PersonCreate):
    """
    Servicio para crear una nueva persona/cliente.
    """
    with Session(engine) as session:
        # Verificar si ya existe una persona con el mismo documento
        existing_person = (
            session.query(Person)
            .filter(
                Person.document_type == person_data.document_type,
                Person.document_number == person_data.document_number,
            )
            .first()
        )

        if existing_person:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe una persona con {person_data.document_type}: {person_data.document_number}",
            )

        # Crear nueva persona
        new_person = Person(
            name=person_data.name,
            last_name=person_data.last_name,
            document_type=person_data.document_type.upper(),
            document_number=person_data.document_number,
        )

        session.add(new_person)
        session.commit()
        session.refresh(new_person)

        return {
            "id": new_person.id,
            "name": new_person.name,
            "last_name": new_person.last_name,
            "document_type": new_person.document_type,
            "document_number": new_person.document_number,
            "full_name": f"{new_person.name} {new_person.last_name}",
        }


def get_all_persons_service():
    """
    Servicio para obtener todas las personas.
    """
    with Session(engine) as session:
        persons = session.query(Person).all()
        return [
            {
                "id": person.id,
                "name": person.name,
                "last_name": person.last_name,
                "document_type": person.document_type,
                "document_number": person.document_number,
                "full_name": f"{person.name} {person.last_name}",
            }
            for person in persons
        ]


def get_person_by_id_service(person_id: uuid.UUID):
    """
    Servicio para obtener una persona por ID.
    """
    with Session(engine) as session:
        person = session.query(Person).filter(Person.id == person_id).first()
        if not person:
            raise HTTPException(status_code=404, detail="Persona no encontrada")

        return {
            "id": person.id,
            "name": person.name,
            "last_name": person.last_name,
            "document_type": person.document_type,
            "document_number": person.document_number,
            "full_name": f"{person.name} {person.last_name}",
        }


def update_person_service(person_id: uuid.UUID, person_data: PersonUpdate):
    """
    Servicio para actualizar una persona.
    """
    with Session(engine) as session:
        person = session.query(Person).filter(Person.id == person_id).first()
        if not person:
            raise HTTPException(status_code=404, detail="Persona no encontrada")

        # Verificar duplicados si se actualizan documento
        if person_data.document_type and person_data.document_number:
            existing_person = (
                session.query(Person)
                .filter(
                    Person.document_type == person_data.document_type,
                    Person.document_number == person_data.document_number,
                    Person.id != person_id,
                )
                .first()
            )

            if existing_person:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ya existe otra persona con {person_data.document_type}: {person_data.document_number}",
                )

        # Actualizar campos
        update_data = person_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "document_type" and value:
                setattr(person, field, value.upper())
            else:
                setattr(person, field, value)

        session.commit()
        session.refresh(person)

        return {
            "id": person.id,
            "name": person.name,
            "last_name": person.last_name,
            "document_type": person.document_type,
            "document_number": person.document_number,
            "full_name": f"{person.name} {person.last_name}",
        }


def search_persons_service(search_term: str):
    """
    Servicio para buscar personas por nombre, apellido o documento.
    """
    with Session(engine) as session:
        persons = (
            session.query(Person)
            .filter(
                or_(
                    Person.name.ilike(f"%{search_term}%"),
                    Person.last_name.ilike(f"%{search_term}%"),
                    Person.document_number.ilike(f"%{search_term}%"),
                )
            )
            .all()
        )

        return [
            {
                "id": person.id,
                "name": person.name,
                "last_name": person.last_name,
                "document_type": person.document_type,
                "document_number": person.document_number,
                "full_name": f"{person.name} {person.last_name}",
            }
            for person in persons
        ]
