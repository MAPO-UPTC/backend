"""
Migración para crear las tablas de inventario y ventas
"""
from sqlalchemy import text

def create_inventory_sales_tables_migration(connection):
    """
    Crear las tablas necesarias para inventario y ventas
    """
    
    # Crear tabla lot si no existe
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS lot (
            id TEXT PRIMARY KEY,
            supplier_name TEXT NOT NULL,
            purchase_date TIMESTAMP NOT NULL,
            invoice_number TEXT,
            total_cost REAL NOT NULL,
            notes TEXT
        )
    """))
    
    # Actualizar tabla lot_detail con nuevos campos
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS lot_detail_new (
            id TEXT PRIMARY KEY,
            lot_id TEXT NOT NULL,
            presentation_id INTEGER NOT NULL,
            quantity_received INTEGER NOT NULL,
            quantity_available INTEGER NOT NULL,
            unit_cost REAL NOT NULL,
            batch_number TEXT,
            expiry_date TIMESTAMP,
            supplier_info TEXT,
            FOREIGN KEY (presentation_id) REFERENCES product_presentation (id)
        )
    """))
    
    # Migrar datos existentes si la tabla vieja existe
    try:
        connection.execute(text("""
            INSERT INTO lot_detail_new (id, lot_id, presentation_id, quantity_received, quantity_available, unit_cost, batch_number)
            SELECT id, lot_id, presentation_id, quantity_received, quantity_available, unit_cost, batch_number
            FROM lot_detail
        """))
        
        # Eliminar tabla vieja y renombrar
        connection.execute(text("DROP TABLE lot_detail"))
        connection.execute(text("ALTER TABLE lot_detail_new RENAME TO lot_detail"))
    except:
        # Si no existe la tabla vieja, solo renombrar
        connection.execute(text("ALTER TABLE lot_detail_new RENAME TO lot_detail"))
    
    # Crear tabla sale si no existe
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS sale (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_code TEXT NOT NULL UNIQUE,
            sale_date TIMESTAMP NOT NULL,
            customer_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            total REAL NOT NULL,
            notes TEXT
        )
    """))
    
    # Crear tabla sale_detail si no existe
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS sale_detail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            presentation_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            discount REAL DEFAULT 0,
            subtotal REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sale (id),
            FOREIGN KEY (presentation_id) REFERENCES product_presentation (id)
        )
    """))
    
    print("✅ Tablas de inventario y ventas creadas/actualizadas exitosamente")

if __name__ == "__main__":
    from src.database import engine
    
    with engine.connect() as connection:
        with connection.begin():
            create_inventory_sales_tables_migration(connection)