#!/usr/bin/env python3
"""
Comandos de utilidad para el proyecto.
"""

import os
import subprocess
import sys
from pathlib import Path


def generate_models_from_db():
    """Genera modelos SQLAlchemy desde la base de datos."""
    print("🔄 Generando modelos desde la base de datos...")
    cmd = [
        "sqlacodegen", 
        "postgresql://mapo:a123@localhost:5432/mapo-dev",
        "--outfile", "models_db.py"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Modelos generados en models_db.py")
    else:
        print("❌ Error generando modelos:", result.stderr)


def generate_pydantic_schemas():
    """Genera esquemas Pydantic desde los modelos."""
    print("🔄 Generando esquemas Pydantic...")
    try:
        from generate_schemas import generate_all_schemas
        schema_content = generate_all_schemas()
        
        os.makedirs("schemas", exist_ok=True)
        with open("schemas/generated_schemas.py", "w", encoding="utf-8") as f:
            f.write(schema_content)
        
        print("✅ Esquemas Pydantic generados en schemas/generated_schemas.py")
    except Exception as e:
        print(f"❌ Error generando esquemas: {e}")


def generate_all():
    """Genera modelos y esquemas automáticamente."""
    print("🚀 Generando modelos y esquemas automáticamente...\n")
    generate_models_from_db()
    print()
    generate_pydantic_schemas()
    print("\n✅ Generación completa!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "models":
            generate_models_from_db()
        elif command == "schemas":
            generate_pydantic_schemas()
        elif command == "all":
            generate_all()
        else:
            print("Comandos disponibles:")
            print("  python manage.py models   - Genera modelos SQLAlchemy")
            print("  python manage.py schemas  - Genera esquemas Pydantic")
            print("  python manage.py all      - Genera todo")
    else:
        generate_all()