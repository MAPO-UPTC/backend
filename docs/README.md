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

## 📚 Documentación Detallada

### Sistema de Ventas

#### 🚀 Inicio Rápido
- **[SWAGGER_EXAMPLES.md](./SWAGGER_EXAMPLES.md)** - ⭐ **EJEMPLOS JSON PARA SWAGGER**
  - JSONs listos para copiar y pegar
  - Cómo obtener UUIDs reales de clientes y productos
  - Ejemplos con cURL y PowerShell
  - Checklist de validación pre-venta
  
- **[FRONTEND_QUICK_SALE_GUIDE.md](./FRONTEND_QUICK_SALE_GUIDE.md)** - Guía de Implementación Frontend
  - Guía paso a paso para implementar ventas
  - Código React/TypeScript completo
  - Hook `useSales` personalizado
  - Errores comunes y soluciones

#### 📖 Documentación Completa
- **[SALES_SYSTEM_COMPLETE_GUIDE.md](./SALES_SYSTEM_COMPLETE_GUIDE.md)** - Guía completa del sistema
  - 8 endpoints documentados con ejemplos
  - Componentes React listos para usar
  - Servicios JavaScript/TypeScript
  - Manejo de errores y validaciones
  - Dashboard de ventas completo

- **[SALES_HISTORY_GUIDE.md](./SALES_HISTORY_GUIDE.md)** - 📊 **Historial de Ventas**
  - Filtros por fecha (opcionales)
  - Paginación y ordenamiento automático
  - Hook `useSalesHistory` completo
  - Componentes con selector de fechas
  - Ejemplos de filtros predefinidos (hoy, semana, mes)

#### 🔀 Ventas Mixtas
- **[MIXED_SALES_GUIDE.md](./MIXED_SALES_GUIDE.md)** - Ventas Mixtas (Empaquetado + Granel)
  - Sistema automático FIFO
  - Ejemplos prácticos de ventas mixtas
  - Componente SaleConfirmation
  - FAQ y casos de uso

#### 🔧 Solución de Problemas
- **[FIX_AUTH_ERROR_401.md](./FIX_AUTH_ERROR_401.md)** - ⚠️ **ERROR 401: Authentication required**
  - Solución completa para error de autenticación
  - 5 opciones según tu cliente API (Fetch, Axios, etc.)
  - Código corregido listo para usar
  - Diagnóstico paso a paso
  - Checklist de verificación

- **[FIX_SALES_ITEMS.md](./FIX_SALES_ITEMS.md)** - 🔧 **Items vacíos en historial de ventas**
  - Corrección de relación Sale ↔ SaleDetail
  - Carga automática de items con lazy="joined"
  - Ejemplos de uso en frontend
  - Verificación post-corrección

---

### ⚠️ IMPORTANTE: Campo Correcto para Ventas

```json
{
  "customer_id": "uuid-del-cliente",  // ✅ CORRECTO
  "client_id": "..."                  // ❌ INCORRECTO
}
```

**Usa `customer_id` en todas las peticiones de ventas.**
