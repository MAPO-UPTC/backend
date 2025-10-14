# ====================================
# DOCKERFILE PARA MAPO BACKEND API
# ====================================

# Usar imagen oficial de Python 3.9 (compatible con tu proyecto)
FROM python:3.9-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Crear usuario no-root por seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación (contenido de src/ directamente a /app/)
COPY src/ ./

# Crear directorio de logs con permisos correctos
RUN mkdir -p logs && chmod 755 logs

# Cambiar permisos y propietario
RUN chown -R appuser:appuser /app
USER appuser

# Exponer puerto
EXPOSE 8000

# Comando de salud para Docker
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Establecer PYTHONPATH para encontrar módulos
ENV PYTHONPATH=/app

# Comando por defecto - ejecutar uvicorn directamente
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
