#!/bin/bash
# ====================================
# SCRIPT DE INICIO PARA PRODUCCIÓN
# ====================================

set -e

echo "🚀 Iniciando MAPO Backend API..."

# Validar variables de entorno críticas
if [[ -z "$DATABASE_URL" ]]; then
    echo "❌ Error: DATABASE_URL no está configurada"
    exit 1
fi

if [[ -z "$FIREBASE_PROJECT_ID" ]]; then
    echo "❌ Error: FIREBASE_PROJECT_ID no está configurada"
    exit 1
fi

echo "✅ Variables de entorno validadas"

# Esperar a que la base de datos esté disponible
echo "⏳ Esperando conexión a la base de datos..."
python -c "
import sys
import time
import psycopg2
from urllib.parse import urlparse

def wait_for_db(database_url, max_retries=30):
    parsed = urlparse(database_url)
    
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path.lstrip('/')
            )
            conn.close()
            print('✅ Base de datos conectada')
            return True
        except Exception as e:
            if attempt == max_retries - 1:
                print(f'❌ Error conectando a la base de datos: {e}')
                sys.exit(1)
            print(f'⏳ Intento {attempt + 1}/{max_retries}: {e}')
            time.sleep(2)

wait_for_db('$DATABASE_URL')
"

# Crear tablas si no existen
echo "🔧 Creando tablas de base de datos..."
python -c "
from models_db import Base
from database import engine
Base.metadata.create_all(engine)
print('✅ Tablas creadas/verificadas')
"

# Ejecutar seeders si es necesario
if [[ "$ENVIRONMENT" == "development" ]] || [[ "$RUN_SEEDERS" == "true" ]]; then
    echo "🌱 Ejecutando seeders..."
    python seed_roles.py || echo "⚠️ Advertencia: Error ejecutando seeders"
fi

echo "🎯 Iniciando servidor..."

# Determinar configuración según el entorno
if [[ "$ENVIRONMENT" == "development" ]]; then
    echo "🔧 Modo desarrollo"
    exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --reload --log-level debug
else
    echo "🚀 Modo producción"
    exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-4} --log-level ${LOG_LEVEL:-info}
fi