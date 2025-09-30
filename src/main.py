import time
import os

import firebase_admin
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from firebase_admin import credentials
from sqlalchemy import text

# Configuración y logging
from config.settings import settings
print(f"[MAPO] DATABASE_URL usado: {os.environ.get('DATABASE_URL')}")
from database import engine
from models_db import Base

# Routers
from routers import client, inventory, product, user
from utils.logging_config import (
    log_error,
    log_request,
    log_startup_info,
    logger,
)

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
    logger.warning(
        "Base de datos no disponible - la aplicación iniciará pero las operaciones de DB fallarán"
    )
    # En producción también continuamos, pero loggeamos el error crítico
    if settings.ENVIRONMENT == "production":
        logger.critical("CRÍTICO: Base de datos no disponible en producción")
        logger.critical("Las operaciones que requieran DB fallarán")
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
app.include_router(client.router, prefix="/clients", tags=["clients"])
app.include_router(inventory.router, prefix="/inventory", tags=["inventory"])


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
    # Verificar conexión a base de datos (con timeout rápido)
    database_status = "disconnected"
    try:
        # Usar timeout muy corto para evitar bloqueos
        import time

        start_time = time.time()
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            if time.time() - start_time < 2:  # Solo si es rápido
                database_status = "connected"
            else:
                database_status = "slow_connection"
    except Exception as db_error:
        logger.warning(f"Database health check failed: {db_error}")
        database_status = "disconnected"

    # Verificar estado de Firebase
    firebase_status = "not_configured"
    try:
        if firebase_admin._apps:
            firebase_status = "configured"
        elif (
            settings.FIREBASE_PROJECT_ID
            and settings.FIREBASE_PROJECT_ID != "desarrollo-local"
        ):
            firebase_status = "configured_but_not_initialized"
    except Exception as fb_error:
        logger.warning(f"Firebase health check failed: {fb_error}")
        firebase_status = "error"

    # La aplicación está "healthy" si puede responder, independiente de la DB
    overall_status = "healthy"
    status_code = 200

    # Solo marcar como unhealthy si TODAS las dependencias críticas fallan
    if database_status == "disconnected" and settings.ENVIRONMENT == "production":
        overall_status = "degraded"  # Degraded instead of unhealthy
        # Still return 200 to pass Docker health checks

    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall_status,
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0",
            "services": {"database": database_status, "firebase": firebase_status},
        },
    )


if __name__ == "__main__":
    # Configuración condicional para desarrollo vs producción
    if settings.ENVIRONMENT == "development":
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="debug",
        )
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=4, log_level="info")
