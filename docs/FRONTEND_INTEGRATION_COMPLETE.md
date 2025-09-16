# 🚀 MAPO Backend - Guía Completa de Integración Frontend

## 📋 Información del Backend

### **🌐 URL del Servidor de Desarrollo:**
```
http://142.93.187.32:8000
```

### **📊 Estado Actual:**
- ✅ **Backend**: Funcionando en DigitalOcean
- ✅ **Base de Datos**: PostgreSQL 17 conectada
- ✅ **Autenticación**: Firebase integrado
- ✅ **CORS**: Configurado para desarrollo y Netlify
- ✅ **Documentación**: http://142.93.187.32:8000/docs

---

## 🔧 Configuración Rápida

### **Variables de Entorno:**

#### **Para React/Next.js:**
```env
# .env.development (desarrollo local)
REACT_APP_API_BASE_URL=http://142.93.187.32:8000
REACT_APP_ENVIRONMENT=development

# .env.production (Netlify/producción)
REACT_APP_API_BASE_URL=http://142.93.187.32:8000
REACT_APP_ENVIRONMENT=production
```

#### **Para Vue/Vite:**
```env
# .env.development
VITE_API_BASE_URL=http://142.93.187.32:8000
VITE_ENVIRONMENT=development

# .env.production
VITE_API_BASE_URL=http://142.93.187.32:8000
VITE_ENVIRONMENT=production
```

#### **Para Angular:**
```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://142.93.187.32:8000',
};

// src/environments/environment.prod.ts
export const environment = {
  production: true,
  apiUrl: 'http://142.93.187.32:8000',
};
```

---

## 📝 Código Listo para Usar

### **1. Cliente API Universal (JavaScript)**

```javascript
// api/client.js
class MapoApiClient {
  constructor() {
    // Detectar automáticamente la URL base
    this.baseURL = this.getApiBaseUrl();
    console.log('🔗 MAPO API URL:', this.baseURL);
  }

  getApiBaseUrl() {
    // Prioridad: Variables de entorno → Fallback
    if (typeof process !== 'undefined' && process.env) {
      // Node.js/Build environment
      return process.env.REACT_APP_API_BASE_URL || 
             process.env.VITE_API_BASE_URL || 
             process.env.NEXT_PUBLIC_API_URL || 
             'http://142.93.187.32:8000';
    }
    
    // Browser environment
    return 'http://142.93.187.32:8000';
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    console.log(`🚀 API Request: ${options.method || 'GET'} ${url}`);

    try {
      const response = await fetch(url, config);
      
      console.log(`📡 Response: ${response.status} ${response.statusText}`);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Success:', data);
      return data;
    } catch (error) {
      console.error('❌ API Error:', error);
      throw error;
    }
  }

  // Métodos de conveniencia
  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT', 
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

// Instancia global
export const mapoApi = new MapoApiClient();
```

### **2. Servicio de Autenticación**

```javascript
// services/authService.js
import { mapoApi } from '../api/client.js';

export class AuthService {
  constructor() {
    this.tokenKey = 'mapo_auth_token';
  }

  async signup(userData) {
    try {
      console.log('📝 Registrando usuario:', userData.email);
      
      const response = await mapoApi.post('/users/signup', userData);
      
      console.log('✅ Usuario registrado exitosamente:', response);
      return response;
    } catch (error) {
      console.error('❌ Error en registro:', error.message);
      
      // Errores específicos de Firebase
      if (error.message.includes('EMAIL_EXISTS')) {
        throw new Error('Este email ya está registrado. Intenta con otro email.');
      }
      
      if (error.message.includes('WEAK_PASSWORD')) {
        throw new Error('La contraseña debe tener al menos 6 caracteres.');
      }
      
      if (error.message.includes('INVALID_EMAIL')) {
        throw new Error('El formato del email no es válido.');
      }
      
      throw error;
    }
  }

  async login(email, password) {
    try {
      console.log('🔐 Iniciando sesión:', email);
      
      const response = await mapoApi.post('/users/login', { email, password });
      
      if (response.token) {
        localStorage.setItem(this.tokenKey, response.token);
        console.log('✅ Login exitoso');
      }
      
      return response;
    } catch (error) {
      console.error('❌ Error en login:', error.message);
      throw error;
    }
  }

  async validateToken() {
    const token = this.getToken();
    if (!token) return false;

    try {
      await mapoApi.post('/users/ping', {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return true;
    } catch (error) {
      this.logout();
      return false;
    }
  }

  getToken() {
    return localStorage.getItem(this.tokenKey);
  }

  logout() {
    localStorage.removeItem(this.tokenKey);
  }

  isAuthenticated() {
    return !!this.getToken();
  }
}

export const authService = new AuthService();
```

### **3. Servicio de Productos**

```javascript
// services/productService.js
import { mapoApi } from '../api/client.js';

export class ProductService {
  async getProducts() {
    console.log('📦 Obteniendo productos...');
    return await mapoApi.get('/products/');
  }

  async getProduct(id) {
    console.log(`📦 Obteniendo producto: ${id}`);
    return await mapoApi.get(`/products/${id}`);
  }

  async createProduct(productData) {
    console.log('📦 Creando producto...');
    return await mapoApi.post('/products/', productData);
  }

  async updateProduct(id, productData) {
    console.log(`📦 Actualizando producto: ${id}`);
    return await mapoApi.put(`/products/${id}`, productData);
  }

  async deleteProduct(id) {
    console.log(`📦 Eliminando producto: ${id}`);
    return await mapoApi.delete(`/products/${id}`);
  }
}

export const productService = new ProductService();
```

---

## 🧪 Ejemplos de Uso

### **1. Registro de Usuario (React)**

```jsx
// components/RegisterForm.jsx
import { useState } from 'react';
import { authService } from '../services/authService';

export function RegisterForm() {
  const [formData, setFormData] = useState({
    name: '',
    last_name: '',
    document_type: 'CC',
    document_number: '',
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await authService.signup(formData);
      setSuccess(`¡Usuario registrado exitosamente! ID: ${response.user_id}`);
      
      // Limpiar formulario
      setFormData({
        name: '',
        last_name: '',
        document_type: 'CC',
        document_number: '',
        email: '',
        password: ''
      });
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Nombre:</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          required
        />
      </div>
      
      <div>
        <label>Apellido:</label>
        <input
          type="text"
          value={formData.last_name}
          onChange={(e) => setFormData({...formData, last_name: e.target.value})}
          required
        />
      </div>
      
      <div>
        <label>Tipo de Documento:</label>
        <select
          value={formData.document_type}
          onChange={(e) => setFormData({...formData, document_type: e.target.value})}
        >
          <option value="CC">Cédula de Ciudadanía</option>
          <option value="TI">Tarjeta de Identidad</option>
          <option value="CE">Cédula de Extranjería</option>
          <option value="PP">Pasaporte</option>
        </select>
      </div>
      
      <div>
        <label>Número de Documento:</label>
        <input
          type="text"
          value={formData.document_number}
          onChange={(e) => setFormData({...formData, document_number: e.target.value})}
          required
        />
      </div>
      
      <div>
        <label>Email:</label>
        <input
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({...formData, email: e.target.value})}
          required
        />
      </div>
      
      <div>
        <label>Contraseña:</label>
        <input
          type="password"
          value={formData.password}
          onChange={(e) => setFormData({...formData, password: e.target.value})}
          required
        />
      </div>
      
      <button type="submit" disabled={loading}>
        {loading ? 'Registrando...' : 'Registrar'}
      </button>
      
      {error && <div style={{color: 'red'}}>{error}</div>}
      {success && <div style={{color: 'green'}}>{success}</div>}
    </form>
  );
}
```

### **2. Lista de Productos (Vue)**

```vue
<!-- components/ProductList.vue -->
<template>
  <div>
    <h2>Productos</h2>
    
    <div v-if="loading">Cargando productos...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else>
      <div v-for="product in products" :key="product.id" class="product-card">
        <h3>{{ product.name }}</h3>
        <p>{{ product.description }}</p>
        <img v-if="product.image_url" :src="product.image_url" :alt="product.name" />
      </div>
    </div>
  </div>
</template>

<script>
import { productService } from '../services/productService.js';

export default {
  name: 'ProductList',
  data() {
    return {
      products: [],
      loading: true,
      error: null
    };
  },
  async mounted() {
    try {
      this.products = await productService.getProducts();
    } catch (error) {
      this.error = error.message;
      console.error('Error loading products:', error);
    } finally {
      this.loading = false;
    }
  }
};
</script>

<style scoped>
.product-card {
  border: 1px solid #ddd;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 8px;
}

.error {
  color: red;
  padding: 1rem;
  background: #ffebee;
  border-radius: 4px;
}
</style>
```

---

## 🧪 Script de Testing

Crea un archivo `test-api.html` para probar la conexión:

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAPO API Test</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .test-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .result { margin-top: 10px; padding: 10px; border-radius: 4px; font-family: monospace; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>🧪 MAPO API - Test de Conectividad</h1>
    
    <div class="test-section">
        <h3>1. Test de Conectividad</h3>
        <button onclick="testConnection()">Probar Conexión</button>
        <div id="connection-result"></div>
    </div>
    
    <div class="test-section">
        <h3>2. Test de Registro</h3>
        <button onclick="testRegistration()">Probar Registro</button>
        <div id="registration-result"></div>
    </div>
    
    <div class="test-section">
        <h3>3. Test de Productos</h3>
        <button onclick="testProducts()">Probar Productos</button>
        <div id="products-result"></div>
    </div>

    <script>
        const API_URL = 'http://142.93.187.32:8000';

        async function testConnection() {
            const resultDiv = document.getElementById('connection-result');
            resultDiv.innerHTML = '<div class="result">Probando conexión...</div>';
            
            try {
                const response = await fetch(`${API_URL}/health`);
                const data = await response.json();
                
                resultDiv.innerHTML = `<div class="result success">
✅ Conexión exitosa!<br>
Status: ${data.status}<br>
Environment: ${data.environment}<br>
Database: ${data.services?.database}<br>
Firebase: ${data.services?.firebase}
                </div>`;
            } catch (error) {
                resultDiv.innerHTML = `<div class="result error">❌ Error de conexión: ${error.message}</div>`;
            }
        }

        async function testRegistration() {
            const resultDiv = document.getElementById('registration-result');
            resultDiv.innerHTML = '<div class="result">Probando registro...</div>';
            
            const userData = {
                name: 'Test',
                last_name: 'User',
                document_type: 'CC',
                document_number: Date.now().toString(),
                email: `test-${Date.now()}@example.com`,
                password: 'password123'
            };
            
            try {
                const response = await fetch(`${API_URL}/users/signup`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(userData)
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    resultDiv.innerHTML = `<div class="result success">
✅ Registro exitoso!<br>
User ID: ${data.user_id}<br>
Email: ${userData.email}
                    </div>`;
                } else {
                    resultDiv.innerHTML = `<div class="result error">❌ Error de registro: ${data.detail}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="result error">❌ Error de registro: ${error.message}</div>`;
            }
        }

        async function testProducts() {
            const resultDiv = document.getElementById('products-result');
            resultDiv.innerHTML = '<div class="result">Cargando productos...</div>';
            
            try {
                const response = await fetch(`${API_URL}/products/`);
                const products = await response.json();
                
                resultDiv.innerHTML = `<div class="result success">
✅ Productos cargados!<br>
Total: ${products.length} productos<br>
Productos: ${products.map(p => p.name).join(', ') || 'No hay productos'}
                </div>`;
            } catch (error) {
                resultDiv.innerHTML = `<div class="result error">❌ Error cargando productos: ${error.message}</div>`;
            }
        }

        // Auto-test connection on load
        window.onload = () => testConnection();
    </script>
</body>
</html>
```

---

## 📊 Endpoints Disponibles

### **🔐 Autenticación:**
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| `POST` | `/users/signup` | Registro de usuario | No |
| `POST` | `/users/login` | Inicio de sesión | No |
| `POST` | `/users/ping` | Validar token | Sí |

### **👥 Usuarios:**
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| `GET` | `/users/` | Listar usuarios | Sí |
| `GET` | `/users/{id}` | Obtener usuario | Sí |
| `PUT` | `/users/{id}` | Actualizar usuario | Sí |
| `GET` | `/users/me/profile` | Mi perfil | Sí |

### **📦 Productos:**
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| `GET` | `/products/` | Listar productos | No |
| `POST` | `/products/` | Crear producto | Sí |
| `GET` | `/products/{id}` | Obtener producto | No |
| `PUT` | `/products/{id}` | Actualizar producto | Sí |
| `DELETE` | `/products/{id}` | Eliminar producto | Sí |

---

## 🚀 Deploy en Netlify

### **1. Configuración de Build:**

```toml
# netlify.toml
[build]
  publish = "dist"  # o "build" según tu framework

[build.environment]
  REACT_APP_API_BASE_URL = "http://142.93.187.32:8000"
  VITE_API_BASE_URL = "http://142.93.187.32:8000"
```

### **2. Variables de Entorno en Netlify:**
1. Ve a: **Site Settings → Environment Variables**
2. Añade: `REACT_APP_API_BASE_URL` = `http://142.93.187.32:8000`
3. Añade: `VITE_API_BASE_URL` = `http://142.93.187.32:8000`

---

## ⚠️ Errores Comunes y Soluciones

### **❌ `EMAIL_EXISTS`**
```javascript
// Solución: Usar emails únicos
const uniqueEmail = `user-${Date.now()}@example.com`;
```

### **❌ `CORS policy error`**
```javascript
// El backend ya está configurado para Netlify
// Si ves este error, verifica la URL
const API_URL = 'http://142.93.187.32:8000'; // ✅ Correcto
const API_URL = 'https://142.93.187.32:8000'; // ❌ No hay HTTPS aún
```

### **❌ `Failed to fetch`**
```javascript
// Verificar conectividad
fetch('http://142.93.187.32:8000/health')
  .then(res => res.json())
  .then(data => console.log('Backend OK:', data))
  .catch(err => console.error('Backend Error:', err));
```

---

## 📞 Soporte y Testing

### **🔗 Enlaces Útiles:**
- **API Docs**: http://142.93.187.32:8000/docs
- **Health Check**: http://142.93.187.32:8000/health
- **OpenAPI JSON**: http://142.93.187.32:8000/openapi.json

### **📧 Para Reportar Problemas:**
Incluir:
1. URL del endpoint
2. Método HTTP usado
3. Headers enviados
4. Body de la request
5. Response recibido
6. Consola del navegador (F12)

---

**✅ Con esta guía, tu frontend debería funcionar perfectamente tanto en desarrollo como en Netlify.**

**🎯 Si tienes problemas, usa el script de testing primero para identificar la causa específica.**