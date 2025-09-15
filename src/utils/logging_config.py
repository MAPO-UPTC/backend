import logging
import sys
from pathlib import Path
from config.settings import settings


def setup_logging():
    """
    Configurar logging para la aplicación.
    """
    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configurar formato de logs
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Nivel de logging según configuración
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Limpiar handlers existentes
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Crear handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    app_file_handler = logging.FileHandler(log_dir / "app.log")
    app_file_handler.setLevel(logging.INFO)

    error_file_handler = logging.FileHandler(log_dir / "error.log")
    error_file_handler.setLevel(logging.ERROR)

    # Crear formatter
    formatter = logging.Formatter(log_format, date_format)

    # Aplicar formatter a todos los handlers
    console_handler.setFormatter(formatter)
    app_file_handler.setFormatter(formatter)
    error_file_handler.setFormatter(formatter)

    # Configurar el root logger
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_file_handler)
    root_logger.addHandler(error_file_handler)

    # Configurar loggers específicos
    # Reducir verbosidad de librerías externas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # Logger para la aplicación
    app_logger = logging.getLogger("mapo")
    app_logger.setLevel(log_level)

    return app_logger


# Logger global de la aplicación
logger = setup_logging()


def log_startup_info():
    """Log información de inicio de la aplicación"""
    logger = logging.getLogger("mapo")
    logger.info("=" * 50)
    logger.info("INICIANDO MAPO BACKEND API")
    logger.info("=" * 50)
    logger.info(f"Entorno: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    logger.info(f"Firebase Project: {settings.get_firebase_project_id()}")
    logger.info(f"CORS Origins: {settings.get_cors_origins()}")
    logger.info("=" * 50)


def log_request(request, response_time: float = None):
    """
    Log información de requests HTTP.
    """
    if response_time:
        logger.info(f"{request.method} {request.url} - {response_time:.3f}s")
    else:
        logger.info(f"{request.method} {request.url}")


def log_error(error: Exception, context: str = ""):
    """
    Log errores con contexto.
    """
    if context:
        logger.error(f"{context}: {str(error)}")
    else:
        logger.error(f"Error: {str(error)}")

    if settings.DEBUG:
        logger.exception("Stack trace:")


def log_auth_event(user_id: str, event: str, details: str = ""):
    """
    Log eventos de autenticación.
    """
    logger.info(f"AUTH - User {user_id}: {event} {details}")


def log_permission_check(user_id: str, action: str, entity: str, result: bool):
    """
    Log verificaciones de permisos.
    """
    status = "ALLOWED" if result else "DENIED"
    logger.info(f"PERMISSION - User {user_id}: {action} on {entity} - {status}")


def log_database_operation(operation: str, table: str, user_id: str = None):
    """
    Log operaciones de base de datos.
    """
    user_info = f" by user {user_id}" if user_id else ""
    logger.info(f"DB - {operation} on {table}{user_info}")
