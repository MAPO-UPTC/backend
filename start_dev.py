#!/usr/bin/env python3
"""
Script para iniciar el servidor MAPO en modo desarrollo
Estructura reorganizada con src/
"""

import subprocess
import sys
import os
from pathlib import Path
# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    dotenv_path = Path(__file__).parent / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path, override=True)
        print(f"[MAPO] .env cargado desde: {dotenv_path}")
    else:
        print("[MAPO] No se encontró archivo .env en el directorio del backend.")
except ImportError:
    print("[MAPO] python-dotenv no está instalado. Instálalo con: pip install python-dotenv")

def main():
    print("=" * 60)
    print("🚀 MAPO Backend API - Servidor de Desarrollo")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not Path("src/main.py").exists():
        print("❌ Error: No se encuentra src/main.py")
        print("   Ejecuta este script desde el directorio raíz del proyecto")
        return 1
    
    # Verificar entorno virtual
    if not Path("mapo").exists():
        print("❌ Error: No se encuentra el entorno virtual")
        print("   Crea el entorno virtual con: python -m mapo venv")
        return 1
    
    try:
        print("🔧 Configurando entorno de desarrollo...")
        
        # Agregar src al PYTHONPATH
        current_dir = Path.cwd()
        src_path = current_dir / "src"
        
        # Configurar variables de entorno mínimas
        env = os.environ.copy()
        env.setdefault("ENVIRONMENT", "development")
        env.setdefault("DEBUG", "true")
        env.setdefault("SECRET_KEY", "dev-secret-key-change-in-production")
        env.setdefault("DATABASE_URL", "sqlite:///./mapo_dev.db")
        env.setdefault("FIREBASE_PROJECT_ID", "desarrollo-local")
        env["PYTHONPATH"] = str(src_path)
        
        print("🚀 Iniciando servidor FastAPI...")
        print("   🌐 URL: http://localhost:8000")
        print("   📚 Docs: http://localhost:8000/docs")
        print("   ⚡ Hot-reload: Activado")
        print("   ❌ Presiona Ctrl+C para detener")
        print("-" * 60)
        
        # Ejecutar con uvicorn desde src/
        cmd = [
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info",
            "--app-dir", "src"
        ]
        
        subprocess.run(cmd, env=env)
        
    except KeyboardInterrupt:
        print("\n✅ Servidor detenido correctamente")
        return 0
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())