from sqlalchemy import create_engine

# Configuración de la conexión a PostgreSQL
DATABASE_URL = "postgresql://mapo:a123@localhost:5432/mapo-dev"

engine = create_engine(DATABASE_URL)