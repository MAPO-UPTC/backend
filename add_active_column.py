"""
Script para agregar la columna 'active' a la tabla category en PostgreSQL
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import text
from database import engine

def add_active_column():
    """
    Agregar columna 'active' a la tabla Category.
    """
    print("🔄 Agregando columna 'active' a la tabla category...")
    
    with engine.connect() as conn:
        try:
            # Verificar si la columna ya existe
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='category' AND column_name='active'
            """)
            result = conn.execute(check_query)
            has_active = result.fetchone() is not None
            
            if has_active:
                print("✅ La columna 'active' ya existe en la tabla category.")
            else:
                print("➕ Agregando columna 'active'...")
                
                # Agregar columna active
                add_column = text("""
                    ALTER TABLE category 
                    ADD COLUMN active BOOLEAN NOT NULL DEFAULT TRUE
                """)
                conn.execute(add_column)
                conn.commit()
                
                print("✅ Columna 'active' agregada exitosamente!")
                
                # Actualizar registros existentes
                print("📝 Actualizando registros existentes...")
                update_existing = text("""
                    UPDATE category 
                    SET active = TRUE 
                    WHERE active IS NULL
                """)
                conn.execute(update_existing)
                conn.commit()
                
                print("✅ Registros actualizados!")
            
            # Mostrar estructura de la tabla
            print("\n📊 Estructura actual de la tabla category:")
            show_structure = text("""
                SELECT column_name, data_type, is_nullable, column_default 
                FROM information_schema.columns 
                WHERE table_name = 'category'
                ORDER BY ordinal_position
            """)
            result = conn.execute(show_structure)
            for row in result:
                print(f"  - {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
            
            print("\n" + "="*60)
            print("✅ ¡Migración completada exitosamente!")
            print("="*60)
            print("\n📝 Próximos pasos:")
            print("  1. Reinicia el servidor FastAPI (Ctrl+C y volver a iniciar)")
            print("  2. Prueba el endpoint: GET http://localhost:8000/categories/")
            print("  3. Si no hay categorías, ejecuta: POST /categories/setup-petshop-defaults/")
            
        except Exception as e:
            print(f"\n❌ Error durante la migración: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()

if __name__ == "__main__":
    try:
        add_active_column()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
