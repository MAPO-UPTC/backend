# MAPO Backend API

✅ **Estado: FUNCIONAL** - Backend completamente refactorizado con nueva arquitectura

## 🎯 Resumen del Proyecto

Backend API para MAPO desarrollado con FastAPI, PostgreSQL y Firebase Auth. 
Arquitectura modular y normalizada lista para producción.

### 🏗️ Nueva Arquitectura de Base de Datos
```
person (datos personales)
├── id (UUID, PK)
├── name, last_name
├── document_type, document_number

user (autenticación)  
├── id (UUID, PK)
├── uid (Firebase UID)
├── email
└── person_id (FK)

role + user_role (sistema de roles)
```

## 🚀 Quick Start

1. **Activar entorno**: `.\Scripts\activate`
2. **Instalar deps**: `pip install -r requirements.txt`
3. **Ejecutar**: `python -m uvicorn main:app --reload --port 8000`
4. **Docs**: http://localhost:8000/docs

## ✅ Estado Funcional

- [x] **Estructura modular** (routers/services/schemas)
- [x] **Base de datos normalizada** (person + user)  
- [x] **Firebase Auth** (registro/login/validación)
- [x] **CRUD completo** de usuarios
- [x] **Documentación automática** (Swagger)
- [x] **Scripts de testing** y verificación

## 📝 Endpoints Principales

- `POST /signup` - Registro (name, email, document)
- `POST /login` - Login con email/password  
- `GET /users` - Listar usuarios (auth requerida)
- `PUT /users/{id}` - Actualizar usuario
- `GET /docs` - Documentación interactiva
