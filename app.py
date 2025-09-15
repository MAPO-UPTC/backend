#!/usr/bin/env python3
"""
MAPO Backend API - Entry Point
Punto de entrada principal para la aplicación MAPO Backend
"""

# Agregar src/ al path para importaciones
import sys
from pathlib import Path

# Agregar directorio src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Importar aplicación principal desde src/
from main import app

# Exportar app para uvicorn
__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )