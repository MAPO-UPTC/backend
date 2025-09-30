# 🗺️ MAPO Backend API

Sistema backend para la aplicación MAPO (Marketplace de Productos Online) construido con FastAPI, PostgreSQL y Firebase.

## 📁 Estructura del Proyecto

```
backend/
├── 📂 src/                    # Código fuente principal
│   ├── 📂 config/            # Configuración de la aplicación
│   ├── 📂 constants/          # Constantes del sistema
│   ├── 📂 routers/           # Endpoints de la API
│   ├── 📂 schemas/           # Esquemas Pydantic
│   ├── 📂 services/          # Lógica de negocio
│   ├── 📂 utils/             # Utilidades y helpers
│   ├── 📂 user/              # Módulos de usuario
│   ├── 📄 main.py            # Aplicación principal FastAPI
│   ├── 📄 database.py        # Configuración de base de datos
│   ├── 📄 models.py          # Modelos de datos
│   └── 📄 models_db.py       # Modelos de base de datos
├── 📂 tests/                 # Tests unitarios e integración
├── 📂 docs/                  # Documentación del proyecto
├── 📂 scripts/               # Scripts de desarrollo
├── 📂 deployment/            # Archivos Docker y despliegue
├── 📂 logs/                  # Archivos de log
├── 📂 venv/                  # Entorno virtual Python
├── 📄 app.py                 # Punto de entrada (opcional)
├── 📄 start_dev.py           # Script de desarrollo
├── 📄 requirements.txt       # Dependencias Python
├── 📄 .env.example          # Template variables de entorno
└── 📄 README.md             # Este archivo
```

## 🚀 Inicio Rápido

### 1. Clonar e Instalar

```bash
git clone <repository-url>
cd mapo-backend
# ⚠️ Requiere Python 3.9.x
py -3.9 -m venv mapo
mapo\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 3. Ejecutar en Desarrollo
```bash
python start_dev.py
```

### 4. Abrir Documentación
- 🌐 **API**: http://localhost:8000
- 📚 **Docs**: http://localhost:8000/docs
- 🔍 **Health**: http://localhost:8000/health


## 🛠️ Tecnologías

- **🐍 Backend**: FastAPI + Python 3.9.x (⚠️ No compatible con 3.10+)
- **🗄️ Base de Datos**: PostgreSQL / SQLite (desarrollo)
- **🔐 Autenticación**: Firebase Admin SDK
- **🐳 Contenedores**: Docker + Docker Compose
- **☁️ Despliegue**: DigitalOcean App Platform

## 📖 Documentación

- 📋 **[Guía de Despliegue](docs/DEPLOY_GUIDE.md)**
- 🏭 **[Configuración de Producción](docs/PRODUCTION_READY.md)**
- 🔄 **[Cambio de Roles](docs/ROLE_SWITCHING_GUIDE.md)**
- 🌐 **[Integración Frontend](docs/FRONTEND_INTEGRATION_GUIDE.md)**
- 📸 **[Gestión de Imágenes](docs/PRODUCTS_IMAGE_URL_DOCS.md)**

## 🔧 Comandos Útiles

```bash
# Desarrollo
python start_dev.py                    # Iniciar servidor desarrollo
python -m pytest tests/               # Ejecutar tests

# Docker
docker-compose up --build             # Construir y ejecutar
docker-compose -f deployment/docker-compose.prod.yml up -d  # Producción

# Base de datos
python src/database.py                # Inicializar BD (si es necesario)
```

## 📊 Estados de la API

- ✅ **Desarrollo**: Funcionando con SQLite
- ✅ **Staging**: Configurado para PostgreSQL
- ✅ **Producción**: Listo para DigitalOcean

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.

---

**🎯 Hecho con ❤️ para el proyecto MAPO**