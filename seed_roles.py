from sqlalchemy.orm import Session
from database import engine
from models_db import Role
from constants.role import RoleManager, RoleEnum

def seed_roles():
    """Inserta los roles predefinidos en la base de datos"""
    with Session(engine) as session:
        # Verificar si ya existen roles
        existing_roles = session.query(Role).count()
        
        if existing_roles > 0:
            print(f"Ya existen {existing_roles} roles en la base de datos.")
            return
        
        # Insertar todos los roles
        for role_enum, role_uuid in RoleManager.get_all_roles():
            role = Role(
                id=role_uuid,
                name=role_enum.value
            )
            session.add(role)
            print(f"Agregando rol: {role_enum.value} -> {role_uuid}")
        
        session.commit()
        print("✅ Roles insertados correctamente")

if __name__ == "__main__":
    seed_roles()