# Script de inicio para MAPO Backend API
Write-Host "🚀 Iniciando MAPO Backend API..." -ForegroundColor Green

# Verificar si estamos en el entorno virtual
if (-not $env:VIRTUAL_ENV) {
    Write-Host "📦 Activando entorno virtual..." -ForegroundColor Yellow
    
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & "venv\Scripts\Activate.ps1"
    } elseif (Test-Path "Scripts\Activate.ps1") {
        & "Scripts\Activate.ps1"
    } else {
        Write-Host "❌ Error: No se encontró el entorno virtual" -ForegroundColor Red
        Write-Host "📋 Ejecuta primero: python -m venv venv" -ForegroundColor Yellow
        Read-Host "Presiona Enter para continuar"
        exit 1
    }
} else {
    Write-Host "✅ Entorno virtual ya activo" -ForegroundColor Green
}

# Verificar si existe .env
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "⚙️ Copiando .env.example a .env..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
    } else {
        Write-Host "⚠️ Advertencia: No existe archivo .env ni .env.example" -ForegroundColor Yellow
    }
}

Write-Host "🏃 Ejecutando servidor..." -ForegroundColor Green
python main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al ejecutar el servidor" -ForegroundColor Red
    Read-Host "Presiona Enter para continuar"
}