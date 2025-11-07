"""
Script para crear un cliente genérico en la base de datos.
Este cliente se usa para ventas a clientes no registrados.

Ejecutar con: python create_generic_client.py
"""

import os
import sys
import uuid

# Agregar el directorio src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from sqlalchemy.orm import Session

from database import engine
from models_db import Person

# UUID fijo para el cliente genérico (usar siempre el mismo)
GENERIC_CLIENT_UUID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def create_generic_client():
    """
    Crear cliente genérico si no existe.
    """
    with Session(engine) as session:
        # Verificar si ya existe
        existing = session.query(Person).filter(Person.id == GENERIC_CLIENT_UUID).first()

        if existing:
            print(f"✅ Cliente genérico ya existe:")
            print(f"   ID: {existing.id}")
            print(f"   Nombre: {existing.name} {existing.last_name}")
            print(f"   Documento: {existing.document_type} {existing.document_number}")
            return

        # Crear cliente genérico
        generic_client = Person(
            id=GENERIC_CLIENT_UUID,
            name="Cliente",
            last_name="Genérico",
            document_type="CC",
            document_number="0000000000",
        )

        session.add(generic_client)
        session.commit()
        session.refresh(generic_client)

        print("✅ Cliente genérico creado exitosamente:")
        print(f"   ID: {generic_client.id}")
        print(f"   Nombre: {generic_client.name} {generic_client.last_name}")
        print(f"   Documento: {generic_client.document_type} {generic_client.document_number}")
        print("\n📝 Usa este UUID en el frontend para ventas sin cliente registrado:")
        print(f"   {GENERIC_CLIENT_UUID}")


if __name__ == "__main__":
    print("🔧 Creando cliente genérico en la base de datos...\n")
    try:
        create_generic_client()
        print("\n✅ Proceso completado exitosamente")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        print(traceback.format_exc())
        sys.exit(1)
