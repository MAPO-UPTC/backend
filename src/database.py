from sqlalchemy import create_engine
from config.settings import settings

# Configuración de la conexión a PostgreSQL usando variables de entorno
DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)