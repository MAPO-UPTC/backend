from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import settings

# Configuración de la conexión a PostgreSQL usando variables de entorno
DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency para obtener la sesión de base de datos
def get_db():
    """
    Dependency que proporciona una sesión de base de datos.
    Se usa con FastAPI Depends() para inyectar la sesión en los endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
