"""
Script de migración para la tabla product_presentation
Agrega las columnas faltantes: price, sku, active
"""
from sqlalchemy import text
from database import engine

def migrate_product_presentation():
    """
    Migración para agregar columnas faltantes a product_presentation
    """
    migration_queries = [
        # Agregar columna price si no existe
        """
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'product_presentation' 
                AND column_name = 'price'
            ) THEN
                ALTER TABLE product_presentation ADD COLUMN price FLOAT NOT NULL DEFAULT 0.0;
            END IF;
        END $$;
        """,
        
        # Agregar columna sku si no existe
        """
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'product_presentation' 
                AND column_name = 'sku'
            ) THEN
                ALTER TABLE product_presentation ADD COLUMN sku VARCHAR;
            END IF;
        END $$;
        """,
        
        # Agregar columna active si no existe
        """
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'product_presentation' 
                AND column_name = 'active'
            ) THEN
                ALTER TABLE product_presentation ADD COLUMN active INTEGER NOT NULL DEFAULT 1;
            END IF;
        END $$;
        """
    ]
    
    try:
        with engine.connect() as connection:
            for query in migration_queries:
                connection.execute(text(query))
            connection.commit()
            print("✅ Migración de product_presentation completada exitosamente")
            return True
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        return False

if __name__ == "__main__":
    migrate_product_presentation()