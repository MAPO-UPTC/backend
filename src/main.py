import uvicorn
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models_db import Base
from database import engine
import firebase_admin
from firebase_admin import credentials
from sqlalchemy import text

# Routers
from routers import user, product

# Configuración y logging
from config.settings import settings
from utils.logging_config import logger, log_startup_info, log_request, log_error

if not firebase_admin._apps:
    try:
        # Usar configuración desde variables de entorno en lugar de archivo JSON
        firebase_config = settings.get_firebase_service_account_dict()

        # Verificar si Firebase está configurado correctamente
        if (
            firebase_config.get("private_key")
            and firebase_config.get("project_id")
            and firebase_config["project_id"] != "desarrollo-local"
        ):

            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase inicializado correctamente")
        else:
            logger.warning(
                "Firebase no configurado - funcionando en modo desarrollo sin autenticacion"
            )

    except Exception as e:
        logger.warning(f"Error inicializando Firebase: {str(e)}")
        logger.warning("Continuando en modo desarrollo sin Firebase")

# Log información de inicio
log_startup_info()

# Crear las tablas de la base de datos (opcional en desarrollo)
try:
    Base.metadata.create_all(engine)
    logger.info("Base de datos conectada y tablas creadas exitosamente")
except Exception as db_error:
    logger.error(f"Error creando tablas de base de datos: {db_error}")
    if settings.ENVIRONMENT == "production":
        raise
    else:
        logger.warning(
            "Base de datos no disponible - funcionando sin persistencia de datos"
        )

# Configurar FastAPI
app = FastAPI(
    title="MAPO Backend API",
    description="API Backend para el sistema MAPO con autenticación Firebase y sistema de permisos",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,  # Ocultar docs en producción
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS configuration usando variables de entorno
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Permitir GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],  # Permitir headers como Authorization
)


# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log solo si no es health check para evitar spam
        if request.url.path != "/health":
            log_request(request, process_time)

        return response
    except Exception as e:
        process_time = time.time() - start_time
        log_error(e, f"Error procesando request {request.method} {request.url}")

        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )


# Middleware para manejo de errores globales
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_error(exc, f"Error no manejado en {request.method} {request.url}")

    if settings.DEBUG:
        return JSONResponse(status_code=500, content={"detail": str(exc)})
    else:
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )


# Include routers
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(product.router, prefix="/products", tags=["products"])


@app.get("/")
async def root():
    """
    Endpoint raíz de la API.
    """
    return {"message": "Welcome to MAPO Backend API"}


@app.get("/health")
async def health_check():
    """
    Endpoint de salud para monitoreo y balanceadores de carga.
    Verifica conectividad a base de datos y servicios críticos.
    """
    try:
        # Verificar conexión a base de datos
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        # Verificar estado de Firebase
        firebase_status = "not_configured"
        if firebase_admin._apps:
            firebase_status = "configured"
        elif (
            settings.FIREBASE_PROJECT_ID
            and settings.FIREBASE_PROJECT_ID != "desarrollo-local"
        ):
            firebase_status = "configured_but_not_initialized"

        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0",
            "services": {"database": "connected", "firebase": firebase_status},
        }
    except Exception as e:
        log_error(e, "Health check failed")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "environment": settings.ENVIRONMENT,
                "version": "1.0.0",
                "error": str(e) if settings.DEBUG else "Service unavailable",
            },
        )


if __name__ == "__main__":
    # Configuración condicional para desarrollo vs producción
    if settings.ENVIRONMENT == "development":
        uvicorn.run(
            "main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug"
        )
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=4, log_level="info")
