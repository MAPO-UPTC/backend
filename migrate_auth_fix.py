"""
Script de migración para actualizar el esquema de la base de datos
"""
from sqlalchemy import text, MetaData, inspect
from src.database import engine
from src.models_db import Base


def migrate_user_table():
    """
    Migrar la tabla user para agregar la columna firebase_uid
    """
    with engine.connect() as conn:
        # Verificar si la columna ya existe
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('user')]
        
        if 'firebase_uid' not in columns:
            print("Agregando columna firebase_uid...")
            conn.execute(text('''
                ALTER TABLE "user" 
                ADD COLUMN firebase_uid VARCHAR
            '''))
            conn.commit()
            print("Columna firebase_uid agregada exitosamente")
        else:
            print("La columna firebase_uid ya existe")


def migrate_person_table():
    """
    Migrar la tabla person para cambiar identification por document_type y document_number
    """
    with engine.connect() as conn:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('person')]
        
        # Si tiene identification pero no document_type, hacer la migración
        if 'identification' in columns and 'document_type' not in columns:
            print("Migrando tabla person...")
            
            # Agregar nuevas columnas
            conn.execute(text('''
                ALTER TABLE person 
                ADD COLUMN document_type VARCHAR,
                ADD COLUMN document_number VARCHAR
            '''))
            
            # Copiar datos de identification a document_number y poner un valor por defecto en document_type
            conn.execute(text('''
                UPDATE person 
                SET document_number = identification,
                    document_type = 'CC'
                WHERE identification IS NOT NULL
            '''))
            
            # Eliminar la columna antigua (opcional, comentado por seguridad)
            # conn.execute(text('ALTER TABLE person DROP COLUMN identification'))
            
            conn.commit()
            print("Tabla person migrada exitosamente")
        else:
            print("La tabla person ya tiene las columnas correctas")


def run_migration():
    """
    Ejecutar todas las migraciones necesarias
    """
    print("=== INICIANDO MIGRACIONES ===")
    
    try:
        migrate_person_table()
        migrate_user_table()
        
        print("=== MIGRACIONES COMPLETADAS EXITOSAMENTE ===")
        return {"status": "success", "message": "Migraciones completadas"}
        
    except Exception as e:
        print(f"Error en migración: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    run_migration()