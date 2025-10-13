# 🔧 Solución: Error 401 (Unauthorized) en Ventas

## ❌ Error que estás viendo:

```
POST http://localhost:8000/sales/ 401 (Unauthorized)
API Error [/sales/]: Error: Authentication required
```

## 🎯 Causa del Problema

El token de autenticación **NO se está enviando** en el header `Authorization` de las peticiones a `/sales/`.

---

## ✅ Soluciones por Tipo de Cliente API

### **Opción 1: Si usas Fetch directamente**

#### ❌ **INCORRECTO** (sin token):
```typescript
const response = await fetch('http://localhost:8000/sales/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(saleData)
});
```

#### ✅ **CORRECTO** (con token):
```typescript
const response = await fetch('http://localhost:8000/sales/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('token')}`  // ← AGREGAR ESTO
  },
  body: JSON.stringify(saleData)
});
```

---

### **Opción 2: Si usas una clase MAPOAPIClient**

#### 🔍 **Verifica tu archivo `client.ts`** (línea 55-73)

Tu clase debería tener un método `getHeaders()` que incluya el token:

```typescript
// client.ts
class MAPOAPIClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.loadToken(); // ← IMPORTANTE: Cargar token al inicializar
  }

  // ✅ Método para cargar token
  private loadToken(): void {
    this.token = localStorage.getItem('token');
  }

  // ✅ Método para obtener headers con token
  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // ⚠️ RECARGAR token por si cambió
    this.loadToken();

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  // ✅ Método request que usa getHeaders()
  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      ...options,
      headers: {
        ...this.getHeaders(),  // ← USAR getHeaders() aquí
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`❌ API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // ✅ Métodos de conveniencia
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  // ✅ Método para actualizar el token
  setToken(token: string): void {
    this.token = token;
    localStorage.setItem('token', token);
  }

  // ✅ Método para limpiar el token
  clearToken(): void {
    this.token = null;
    localStorage.removeItem('token');
  }
}

export const apiClient = new MAPOAPIClient();
```

---

### **Opción 3: Si usas Axios**

```typescript
// client.ts
import axios, { AxiosInstance } from 'axios';

const apiClient: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// ✅ Interceptor para agregar token automáticamente
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ✅ Interceptor para manejar errores 401
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('❌ No autenticado - redirigiendo a login');
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

---

### **Opción 4: Si usas un servicio de ventas personalizado**

#### 🔍 **Verifica tu archivo `index.ts`** (línea 419)

```typescript
// services/sales/index.ts o similar
export async function createSale(saleData: CreateSaleRequest) {
  const token = localStorage.getItem('token');
  
  if (!token) {
    throw new Error('No hay sesión activa. Por favor inicia sesión.');
  }

  const response = await fetch('http://localhost:8000/sales/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`  // ← AGREGAR ESTO
    },
    body: JSON.stringify(saleData)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al crear venta');
  }

  return await response.json();
}
```

---

### **Opción 5: Si usas React Hook (useSales.ts)**

#### 🔍 **Verifica tu archivo `useSales.ts`** (línea 51)

```typescript
// hooks/useSales.ts
import { useState } from 'react';

export function useSales() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createSale = async (customerId: string, saleItems: any[], notes?: string) => {
    setLoading(true);
    setError(null);

    try {
      // ✅ Obtener token
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No hay sesión activa. Por favor inicia sesión.');
      }

      const response = await fetch('http://localhost:8000/sales/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`  // ← AGREGAR ESTO
        },
        body: JSON.stringify({
          customer_id: customerId,
          sale_items: saleItems,
          notes: notes || ''
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al crear venta');
      }

      const sale = await response.json();
      return sale;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createSale, loading, error };
}
```

---

## 🔍 Cómo Diagnosticar el Problema

### **1. Verifica que el token existe**

Abre la consola del navegador y ejecuta:

```javascript
console.log('Token:', localStorage.getItem('token'));
```

**Resultado esperado:**
```
Token: eyJhbGciOiJSUzI1NiIsImtpZCI6Ij...  (un JWT largo)
```

**Si ves `null`** → No estás guardando el token después del login.

---

### **2. Verifica que el token se envía en el header**

En las DevTools del navegador:
1. Ve a la pestaña **Network**
2. Busca la petición `POST /sales/`
3. Click en la petición
4. Ve a la pestaña **Headers**
5. Busca en **Request Headers**:

**Debe aparecer:**
```
Authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6Ij...
```

**Si NO aparece** → El problema está en tu código frontend.

---

### **3. Verifica que el token es válido**

Prueba con cURL:

```bash
# PowerShell
$token = "TU_TOKEN_AQUI"
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri "http://localhost:8000/users/ping" `
    -Method POST `
    -Headers $headers
```

**Resultado esperado:**
```json
{
  "message": "Token válido",
  "user": { ... }
}
```

**Si falla** → El token está expirado o es inválido.

---

## ✅ Solución Completa Paso a Paso

### **Paso 1: Asegúrate de guardar el token después del login**

```typescript
// Después del login exitoso
const loginResponse = await fetch('http://localhost:8000/users/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});

const data = await loginResponse.json();

// ✅ Guardar token
if (data.token) {
  localStorage.setItem('token', data.token);
  console.log('✅ Token guardado:', data.token);
}
```

---

### **Paso 2: Crea una función helper para obtener headers**

```typescript
// utils/api.ts
export function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('token');
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  } else {
    console.warn('⚠️ No se encontró token - la petición puede fallar');
  }

  return headers;
}
```

---

### **Paso 3: Usa esa función en todas tus peticiones**

```typescript
// En cualquier petición
import { getAuthHeaders } from './utils/api';

const response = await fetch('http://localhost:8000/sales/', {
  method: 'POST',
  headers: getAuthHeaders(),  // ← Usa la función helper
  body: JSON.stringify(saleData)
});
```

---

## 🚨 Errores Comunes

### **Error 1: Token guardado con nombre incorrecto**

```typescript
// ❌ INCORRECTO
localStorage.setItem('authToken', token);

// Pero luego intentas obtenerlo con:
localStorage.getItem('token');  // ← Devuelve null
```

**Solución**: Usa el mismo nombre siempre:
```typescript
const TOKEN_KEY = 'token';  // Constante
localStorage.setItem(TOKEN_KEY, token);
localStorage.getItem(TOKEN_KEY);
```

---

### **Error 2: Token no se actualiza en la clase API**

Si tienes una clase singleton, el token puede no actualizarse:

```typescript
// ❌ PROBLEMA: token se carga solo una vez
class MAPOAPIClient {
  private token: string | null = localStorage.getItem('token');  // Solo se ejecuta una vez
}

// ✅ SOLUCIÓN: recargar token en cada petición
class MAPOAPIClient {
  private getToken(): string | null {
    return localStorage.getItem('token');  // Se ejecuta cada vez
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    const token = this.getToken();  // ← Obtener token fresco
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }
}
```

---

### **Error 3: Endpoint incorrecto**

```typescript
// ❌ INCORRECTO
fetch('http://localhost:8000/sales/')  // Sin /api/v1

// ✅ CORRECTO (verifica en Swagger cuál es el endpoint real)
fetch('http://localhost:8000/api/v1/sales/')  // Con /api/v1
```

---

## 🎯 Código Completo Listo para Usar

### **Cliente API Completo y Funcional**

```typescript
// api/client.ts
class MAPOAPIClient {
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  private getToken(): string | null {
    return localStorage.getItem('token');
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (response.status === 401) {
        console.error('❌ No autenticado - limpiando sesión');
        localStorage.removeItem('token');
        throw new Error('Authentication required');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`❌ API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  setToken(token: string): void {
    localStorage.setItem('token', token);
  }

  clearToken(): void {
    localStorage.removeItem('token');
  }
}

export const apiClient = new MAPOAPIClient();
```

### **Hook de Ventas Completo**

```typescript
// hooks/useSales.ts
import { useState } from 'react';
import { apiClient } from '../api/client';

interface CreateSaleRequest {
  customer_id: string;
  sale_items: Array<{
    product_id: string;
    quantity: number;
    unit_price: number;
  }>;
  notes?: string;
}

export function useSales() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createSale = async (saleData: CreateSaleRequest) => {
    setLoading(true);
    setError(null);

    try {
      const sale = await apiClient.post('/sales/', saleData);
      return sale;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createSale, loading, error };
}
```

---

## 📋 Checklist de Verificación

- [ ] ✅ El token se guarda después del login: `localStorage.setItem('token', token)`
- [ ] ✅ El token existe: `console.log(localStorage.getItem('token'))`
- [ ] ✅ El header se envía: Verificar en DevTools → Network → Headers
- [ ] ✅ El header tiene el formato correcto: `Authorization: Bearer <token>`
- [ ] ✅ El endpoint es correcto: Verificar en Swagger
- [ ] ✅ El token es válido: Probar con `POST /users/ping`
- [ ] ✅ El usuario está autenticado en la sesión actual

---

## 🎉 Resultado Esperado

Después de aplicar la solución, deberías ver:

```
✅ POST http://localhost:8000/sales/ 200 (OK)
✅ Venta creada exitosamente
```

---

¿Necesitas ayuda con tu código específico? Comparte tu `client.ts`, `useSales.ts` o `index.ts` y te ayudo a corregirlo.
