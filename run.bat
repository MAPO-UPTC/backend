@echo off
echo 🚀 Iniciando MAPO Backend API...

REM Verificar si estamos en el entorno virtual
if not defined VIRTUAL_ENV (
    echo 📦 Activando entorno virtual...
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
    ) else if exist "Scripts\activate.bat" (
        call Scripts\activate.bat
    ) else (
        echo ❌ Error: No se encontró el entorno virtual
        echo 📋 Ejecuta primero: python -m venv venv
        pause
        exit /b 1
    )
) else (
    echo ✅ Entorno virtual ya activo
)

REM Verificar si existe .env
if not exist ".env" (
    if exist ".env.example" (
        echo ⚙️ Copiando .env.example a .env...
        copy .env.example .env
    ) else (
        echo ⚠️ Advertencia: No existe archivo .env ni .env.example
    )
)

echo 🏃 Ejecutando servidor...
python main.py

if %ERRORLEVEL% neq 0 (
    echo ❌ Error al ejecutar el servidor
    pause
)