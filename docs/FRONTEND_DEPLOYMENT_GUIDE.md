# 🚀 Guía de Integración Frontend - MAPO Backend en Producción

## 📋 Resumen de Cambios

El backend de MAPO ha sido **completamente desplegado en producción** en DigitalOcean. El frontend debe actualizar sus configuraciones para apuntar al nuevo endpoint de producción.

---

## 🌐 Nueva URL de Producción

### **URL Base de la API:**
```
http://142.93.187.32:8000
```

### **Endpoints Principales:**
- **API Root**: `http://142.93.187.32:8000/`
- **Health Check**: `http://142.93.187.32:8000/health`
- **Documentación Swagger**: `http://142.93.187.32:8000/docs`
- **ReDoc**: `http://142.93.187.32:8000/redoc`
- **OpenAPI JSON**: `http://142.93.187.32:8000/openapi.json`

---

## ⚙️ Configuraciones para el Frontend

### **1. Variables de Entorno**

Actualiza tu archivo `.env` o `.env.production`:

```env
# Producción
REACT_APP_API_BASE_URL=http://142.93.187.32:8000
REACT_APP_API_URL=http://142.93.187.32:8000
VITE_API_BASE_URL=http://142.93.187.32:8000  # Si usas Vite
NEXT_PUBLIC_API_URL=http://142.93.187.32:8000  # Si usas Next.js

# Para desarrollo local (mantener)
# REACT_APP_API_BASE_URL=http://localhost:8000
```

### **2. Archivo de Configuración (config.js/ts)**

```javascript
// config/api.js
const config = {
  development: {
    API_BASE_URL: 'http://localhost:8000',
  },
  production: {
    API_BASE_URL: 'http://142.93.187.32:8000',
  }
};

export const API_BASE_URL = config[process.env.NODE_ENV]?.API_BASE_URL || config.development.API_BASE_URL;
```

### **3. Para Axios/Fetch**

```javascript
// services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://142.93.187.32:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;
```

---

## 🔐 Autenticación y Headers

### **Headers Necesarios:**
```javascript
// Para requests autenticados
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json',
};
```

### **CORS - Configuración Actual:**
El backend está configurado para permitir requests desde:
- `http://142.93.187.32`
- `https://142.93.187.32`

**Si tu frontend está en un dominio diferente**, necesitarás:
1. Informar el dominio del frontend
2. Actualizar la configuración CORS en el backend

---

## 📊 Endpoints Disponibles

### **Autenticación:**
- `POST /users/signup` - Registro de usuarios
- `POST /users/login` - Inicio de sesión
- `POST /users/ping` - Validar token

### **Usuarios:**
- `GET /users/` - Obtener usuarios
- `GET /users/{user_id}` - Obtener usuario por ID
- `PUT /users/{user_id}` - Actualizar usuario
- `GET /users/me/profile` - Perfil del usuario actual
- `GET /users/me/permissions` - Permisos del usuario
- `POST /users/me/switch-role` - Cambiar rol activo

### **Productos:**
- `GET /products/` - Obtener productos (público)
- `POST /products/` - Crear producto (requiere autenticación)
- `GET /products/{product_id}` - Obtener producto por ID
- `PUT /products/{product_id}` - Actualizar producto
- `DELETE /products/{product_id}` - Eliminar producto

---

## 🧪 Pruebas de Conectividad

### **1. Verificar Conectividad Básica:**
```javascript
// Test de conectividad
async function testConnection() {
  try {
    const response = await fetch('http://142.93.187.32:8000/health');
    const data = await response.json();
    console.log('Backend Status:', data);
    return data.status === 'healthy';
  } catch (error) {
    console.error('Error conectando al backend:', error);
    return false;
  }
}
```

### **2. Prueba desde el Navegador:**
Abre la consola del navegador y ejecuta:
```javascript
fetch('http://142.93.187.32:8000/health')
  .then(res => res.json())
  .then(data => console.log(data));
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "firebase": "configured_but_not_initialized"
  }
}
```

---

## 🔄 Proceso de Migración

### **Paso 1: Backup**
Respalda tu configuración actual antes de hacer cambios.

### **Paso 2: Actualizar Variables**
Cambia las URLs en tus archivos de configuración.

### **Paso 3: Probar Localmente**
Ejecuta tu frontend localmente y verifica que se conecte al backend de producción.

### **Paso 4: Desplegar**
Una vez verificado, despliega tu frontend.

---

## 🐛 Resolución de Problemas

### **Error de CORS:**
```
Access to fetch at 'http://142.93.187.32:8000/...' from origin '...' has been blocked by CORS policy
```
**Solución:** Informar el dominio del frontend para añadirlo a la configuración CORS.

### **Error de Red:**
```
TypeError: Failed to fetch
```
**Verificar:**
1. ¿El backend está ejecutándose? → Probar `http://142.93.187.32:8000/health`
2. ¿La URL es correcta?
3. ¿Hay problemas de red/firewall?

### **Error 404 en endpoints:**
**Verificar:**
1. ¿El endpoint existe? → Revisar `http://142.93.187.32:8000/docs`
2. ¿La URL está bien formada?
3. ¿Los parámetros son correctos?

---

## 📞 Contacto y Soporte

### **Estado del Sistema:**
- **URL de Salud**: http://142.93.187.32:8000/health
- **Documentación**: http://142.93.187.32:8000/docs

### **Información Técnica:**
- **Servidor**: DigitalOcean Droplet (Ubuntu)
- **Base de Datos**: PostgreSQL 17
- **Autenticación**: Firebase Admin SDK
- **Framework**: FastAPI + Uvicorn

### **Logs y Monitoreo:**
Para reportar problemas, incluir:
1. URL del endpoint afectado
2. Método HTTP (GET, POST, etc.)
3. Headers enviados
4. Response recibido
5. Timestamp del error

---

## 🚀 Próximos Pasos

1. **HTTPS**: Configurar certificado SSL para usar `https://` en lugar de `http://`
2. **Dominio**: Configurar un dominio personalizado (ej: `api.mapo.com`)
3. **CDN**: Implementar CloudFlare o similar para mejor rendimiento
4. **Monitoreo**: Configurar alertas y métricas de aplicación

---

**✅ El backend está completamente funcional y listo para uso en producción.**

**🔗 Documentación interactiva disponible en: http://142.93.187.32:8000/docs**