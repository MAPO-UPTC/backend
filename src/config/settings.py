import os
from typing import List

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class Settings:
    """
    Configuración centralizada de la aplicación usando variables de entorno.
    """

    # ====================================
    # FIREBASE SERVICE ACCOUNT
    # ====================================
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_PRIVATE_KEY_ID: str = os.getenv("FIREBASE_PRIVATE_KEY_ID", "")
    FIREBASE_PRIVATE_KEY: str = os.getenv("FIREBASE_PRIVATE_KEY", "")
    FIREBASE_CLIENT_EMAIL: str = os.getenv("FIREBASE_CLIENT_EMAIL", "")
    FIREBASE_CLIENT_ID: str = os.getenv("FIREBASE_CLIENT_ID", "")
    FIREBASE_AUTH_URI: str = os.getenv(
        "FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"
    )
    FIREBASE_TOKEN_URI: str = os.getenv(
        "FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"
    )
    FIREBASE_AUTH_PROVIDER_X509_CERT_URL: str = os.getenv(
        "FIREBASE_AUTH_PROVIDER_X509_CERT_URL",
        "https://www.googleapis.com/oauth2/v1/certs",
    )
    FIREBASE_CLIENT_X509_CERT_URL: str = os.getenv("FIREBASE_CLIENT_X509_CERT_URL", "")
    FIREBASE_UNIVERSE_DOMAIN: str = os.getenv(
        "FIREBASE_UNIVERSE_DOMAIN", "googleapis.com"
    )

    # ====================================
    # FIREBASE WEB CONFIG
    # ====================================
    FIREBASE_API_KEY: str = os.getenv("FIREBASE_API_KEY", "")
    FIREBASE_AUTH_DOMAIN: str = os.getenv("FIREBASE_AUTH_DOMAIN", "")
    FIREBASE_STORAGE_BUCKET: str = os.getenv("FIREBASE_STORAGE_BUCKET", "")
    FIREBASE_MESSAGING_SENDER_ID: str = os.getenv("FIREBASE_MESSAGING_SENDER_ID", "")
    FIREBASE_APP_ID: str = os.getenv("FIREBASE_APP_ID", "")
    FIREBASE_MEASUREMENT_ID: str = os.getenv("FIREBASE_MEASUREMENT_ID", "")
    FIREBASE_DATABASE_URL: str = os.getenv("FIREBASE_DATABASE_URL", "")

    # ====================================
    # BASE DE DATOS
    # ====================================
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./mapo_dev.db")

    # ====================================
    # CONFIGURACIÓN DE APLICACIÓN
    # ====================================
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key")

    # ====================================
    # CONFIGURACIÓN DE CORS
    # ====================================
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"),
    ).split(",")

    # ====================================
    # CONFIGURACIÓN ADICIONAL PARA PRODUCCIÓN
    # ====================================
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "4"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    # ====================================
    # CREDENCIALES DE TESTING
    # ====================================
    TEST_ADMIN_EMAIL: str = os.getenv("TEST_ADMIN_EMAIL", "testadmin@example.com")
    TEST_ADMIN_PASSWORD: str = os.getenv("TEST_ADMIN_PASSWORD", "change_this_password")
    TEST_USER_EMAIL: str = os.getenv("TEST_USER_EMAIL", "testuser@example.com")
    TEST_USER_PASSWORD: str = os.getenv("TEST_USER_PASSWORD", "change_this_password")
    TEST_PERMISSIONS_EMAIL: str = os.getenv(
        "TEST_PERMISSIONS_EMAIL", "testpermissions@example.com"
    )
    TEST_PERMISSIONS_PASSWORD: str = os.getenv(
        "TEST_PERMISSIONS_PASSWORD", "change_this_password"
    )

    # ====================================
    # MÉTODOS DE UTILIDAD
    # ====================================

    @classmethod
    def get_firebase_service_account_dict(cls) -> dict:
        """
        Retorna la configuración de Firebase Service Account como diccionario.
        Reemplaza el archivo serviceAccountKey.json
        """
        return {
            "type": "service_account",
            "project_id": cls.FIREBASE_PROJECT_ID,
            "private_key_id": cls.FIREBASE_PRIVATE_KEY_ID,
            "private_key": (
                cls.FIREBASE_PRIVATE_KEY.replace("\\n", "\n")
                if cls.FIREBASE_PRIVATE_KEY
                else ""
            ),
            "client_email": cls.FIREBASE_CLIENT_EMAIL,
            "client_id": cls.FIREBASE_CLIENT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{cls.FIREBASE_CLIENT_EMAIL}",
            "universe_domain": "googleapis.com",
        }

    @classmethod
    def get_firebase_project_id(cls) -> str:
        """Retorna el Project ID de Firebase"""
        return cls.FIREBASE_PROJECT_ID or "desarrollo-local"

    @classmethod
    def get_cors_origins(cls) -> list:
        """Retorna las URLs permitidas para CORS"""
        return cls.ALLOWED_ORIGINS

    @classmethod
    def get_firebase_web_config(cls) -> dict:
        """
        Retorna la configuración web de Firebase.
        """
        return {
            "apiKey": cls.FIREBASE_API_KEY,
            "authDomain": cls.FIREBASE_AUTH_DOMAIN,
            "projectId": cls.FIREBASE_PROJECT_ID,
            "storageBucket": cls.FIREBASE_STORAGE_BUCKET,
            "messagingSenderId": cls.FIREBASE_MESSAGING_SENDER_ID,
            "appId": cls.FIREBASE_APP_ID,
            "measurementId": cls.FIREBASE_MEASUREMENT_ID,
            "databaseURL": cls.FIREBASE_DATABASE_URL,
        }

    @classmethod
    def validate_config(cls) -> bool:
        """
        Valida que las variables de entorno críticas estén configuradas.
        """
        # En desarrollo, solo validamos la base de datos
        if cls.ENVIRONMENT == "development":
            if not cls.DATABASE_URL:
                print("❌ Error: DATABASE_URL es requerida")
                return False
            return True

        # En producción, validamos las variables críticas
        critical_vars = {
            "DATABASE_URL": cls.DATABASE_URL,
        }

        # Firebase es crítico solo si se usa autenticación
        firebase_vars = {
            "FIREBASE_PROJECT_ID": cls.FIREBASE_PROJECT_ID,
            "FIREBASE_PRIVATE_KEY": cls.FIREBASE_PRIVATE_KEY,
            "FIREBASE_CLIENT_EMAIL": cls.FIREBASE_CLIENT_EMAIL,
        }

        missing_critical = [name for name, value in critical_vars.items() if not value]
        missing_firebase = [name for name, value in firebase_vars.items() if not value]

        if missing_critical:
            print(f"❌ Error: Faltan variables de entorno críticas: {missing_critical}")
            return False

        if missing_firebase:
            print(
                f"⚠️  Advertencia: Variables de Firebase faltantes: {missing_firebase}"
            )
            print("🔥 La autenticación Firebase no funcionará correctamente")

        return True


# Instancia global de configuración
settings = Settings()

# Validar configuración al importar
if not settings.validate_config():
    print("⚠️  Advertencia: La configuración no está completa. Revisa tu archivo .env")
