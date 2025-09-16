# 💻 Ejemplos de Código - Integración Frontend con MAPO Backend

## 🎯 Configuraciones por Framework

### **React.js con Axios**

```javascript
// src/config/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://142.93.187.32:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para añadir token automáticamente
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default apiClient;
```

```javascript
// src/services/authService.js
import apiClient from '../config/api';

export class AuthService {
  async login(email, password) {
    try {
      const response = await apiClient.post('/users/login', {
        email,
        password
      });
      
      if (response.data.token) {
        localStorage.setItem('authToken', response.data.token);
      }
      
      return response.data;
    } catch (error) {
      console.error('Login error:', error.response?.data || error.message);
      throw error;
    }
  }

  async signup(userData) {
    try {
      const response = await apiClient.post('/users/signup', userData);
      return response.data;
    } catch (error) {
      console.error('Signup error:', error.response?.data || error.message);
      throw error;
    }
  }

  async validateToken() {
    try {
      const response = await apiClient.post('/users/ping');
      return response.data;
    } catch (error) {
      localStorage.removeItem('authToken');
      throw error;
    }
  }

  logout() {
    localStorage.removeItem('authToken');
  }
}

export const authService = new AuthService();
```

### **Vue.js con Fetch**

```javascript
// src/composables/useApi.js
import { ref } from 'vue';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://142.93.187.32:8000';

export function useApi() {
  const loading = ref(false);
  const error = ref(null);

  const apiRequest = async (endpoint, options = {}) => {
    loading.value = true;
    error.value = null;

    try {
      const token = localStorage.getItem('authToken');
      const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
      };

      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    loading,
    error,
    apiRequest,
  };
}
```

```javascript
// src/services/productService.js
import { useApi } from '@/composables/useApi';

export function useProducts() {
  const { apiRequest, loading, error } = useApi();

  const getProducts = async () => {
    return await apiRequest('/products/');
  };

  const getProduct = async (id) => {
    return await apiRequest(`/products/${id}`);
  };

  const createProduct = async (productData) => {
    return await apiRequest('/products/', {
      method: 'POST',
      body: JSON.stringify(productData),
    });
  };

  const updateProduct = async (id, productData) => {
    return await apiRequest(`/products/${id}`, {
      method: 'PUT',
      body: JSON.stringify(productData),
    });
  };

  const deleteProduct = async (id) => {
    return await apiRequest(`/products/${id}`, {
      method: 'DELETE',
    });
  };

  return {
    loading,
    error,
    getProducts,
    getProduct,
    createProduct,
    updateProduct,
    deleteProduct,
  };
}
```

### **Next.js (App Router)**

```javascript
// lib/api.js
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://142.93.187.32:8000';

export class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
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

    // Añadir token si está disponible (solo en el cliente)
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Métodos de conveniencia
  async get(endpoint, headers = {}) {
    return this.request(endpoint, { method: 'GET', headers });
  }

  async post(endpoint, data, headers = {}) {
    return this.request(endpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data, headers = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      headers,
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint, headers = {}) {
    return this.request(endpoint, { method: 'DELETE', headers });
  }
}

export const apiClient = new ApiClient();
```

```javascript
// app/products/page.js
'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const data = await apiClient.get('/products/');
        setProducts(data);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching products:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (loading) return <div>Cargando productos...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Productos</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {products.map((product) => (
          <div key={product.id} className="border p-4 rounded">
            <h3>{product.name}</h3>
            <p>{product.description}</p>
            {product.image_url && (
              <img 
                src={product.image_url} 
                alt={product.name}
                className="w-full h-48 object-cover mt-2"
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### **Angular (TypeScript)**

```typescript
// src/app/services/api.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseURL = environment.apiUrl || 'http://142.93.187.32:8000';

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    let headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    const token = localStorage.getItem('authToken');
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }

    return headers;
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = error.error.message;
    } else {
      // Server-side error
      errorMessage = error.error?.detail || `Error Code: ${error.status}`;
    }

    console.error('API Error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }

  get<T>(endpoint: string): Observable<T> {
    return this.http.get<T>(`${this.baseURL}${endpoint}`, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  post<T>(endpoint: string, data: any): Observable<T> {
    return this.http.post<T>(`${this.baseURL}${endpoint}`, data, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  put<T>(endpoint: string, data: any): Observable<T> {
    return this.http.put<T>(`${this.baseURL}${endpoint}`, data, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  delete<T>(endpoint: string): Observable<T> {
    return this.http.delete<T>(`${this.baseURL}${endpoint}`, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }
}
```

```typescript
// src/app/services/product.service.ts
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface Product {
  id: string;
  name: string;
  description: string;
  category_id?: string;
  image_url?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ProductService {
  constructor(private apiService: ApiService) {}

  getProducts(): Observable<Product[]> {
    return this.apiService.get<Product[]>('/products/');
  }

  getProduct(id: string): Observable<Product> {
    return this.apiService.get<Product>(`/products/${id}`);
  }

  createProduct(product: Omit<Product, 'id'>): Observable<Product> {
    return this.apiService.post<Product>('/products/', product);
  }

  updateProduct(id: string, product: Partial<Product>): Observable<Product> {
    return this.apiService.put<Product>(`/products/${id}`, product);
  }

  deleteProduct(id: string): Observable<void> {
    return this.apiService.delete<void>(`/products/${id}`);
  }
}
```

## 🔧 Configuración de Variables de Entorno

### **React (.env.development)**
```env
REACT_APP_API_BASE_URL=http://142.93.187.32:8000
REACT_APP_ENVIRONMENT=development
```

### **Vue/Vite (.env.development)**
```env
VITE_API_BASE_URL=http://142.93.187.32:8000
VITE_ENVIRONMENT=development
```

### **Next.js (.env.development)**
```env
NEXT_PUBLIC_API_URL=http://142.93.187.32:8000
NEXT_PUBLIC_ENVIRONMENT=development
```

### **Angular (environment.ts)**
```typescript
export const environment = {
  production: false,
  development: true,
  apiUrl: 'http://142.93.187.32:8000',
};
```

## 🧪 Función de Prueba Universal

```javascript
// Función para probar la conectividad (funciona en cualquier framework)
async function testBackendConnection() {
  const API_URL = 'http://142.93.187.32:8000';
  
  console.log('🔍 Probando conectividad con el backend...');
  
  try {
    // Test 1: Health check
    const healthResponse = await fetch(`${API_URL}/health`);
    const healthData = await healthResponse.json();
    console.log('✅ Health Check:', healthData);
    
    // Test 2: Productos públicos
    const productsResponse = await fetch(`${API_URL}/products/`);
    const productsData = await productsResponse.json();
    console.log('✅ Productos (público):', productsData.length, 'productos encontrados');
    
    // Test 3: OpenAPI spec
    const openApiResponse = await fetch(`${API_URL}/openapi.json`);
    const openApiData = await openApiResponse.json();
    console.log('✅ OpenAPI:', openApiData.info.title, 'v' + openApiData.info.version);
    
    console.log('🎉 ¡Todas las pruebas pasaron! El backend está funcionando correctamente.');
    return true;
    
  } catch (error) {
    console.error('❌ Error conectando al backend:', error);
    return false;
  }
}

// Ejecutar la prueba
testBackendConnection();
```

---

## 📞 Troubleshooting por Framework

### **React Common Issues:**
```javascript
// Error de CORS en desarrollo
// Solución: Proxy en package.json
{
  "name": "my-app",
  "proxy": "http://142.93.187.32:8000",
  // ... resto de configuración
}
```

### **Vue/Vite Proxy:**
```javascript
// vite.config.js
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://142.93.187.32:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
}
```

### **Next.js API Routes:**
```javascript
// pages/api/proxy/[...slug].js
export default async function handler(req, res) {
  const { slug } = req.query;
  const endpoint = Array.isArray(slug) ? slug.join('/') : slug;
  
  const response = await fetch(`http://142.93.187.32:8000/${endpoint}`, {
    method: req.method,
    headers: {
      'Content-Type': 'application/json',
      ...req.headers,
    },
    body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined,
  });
  
  const data = await response.json();
  res.status(response.status).json(data);
}
```

---

**🚀 Con estos ejemplos, cualquier frontend debería poder conectarse exitosamente al backend de MAPO en el entorno de desarrollo/staging.**

---

## 🏭 Configuración Futura para Producción

Cuando se despliegue a producción real, actualizar las URLs a:

### **Variables de Producción:**
```env
# React
REACT_APP_API_BASE_URL=https://api.mapo.com
REACT_APP_ENVIRONMENT=production

# Vue/Vite
VITE_API_BASE_URL=https://api.mapo.com
VITE_ENVIRONMENT=production

# Next.js
NEXT_PUBLIC_API_URL=https://api.mapo.com
NEXT_PUBLIC_ENVIRONMENT=production
```

### **Diferencias Clave en Producción:**
- **HTTPS**: Conexión segura obligatoria
- **Dominio personalizado**: En lugar de IP directa
- **Rate limiting**: Protección contra abuso
- **Logs sanitizados**: Sin información sensible
- **Monitoreo avanzado**: Métricas y alertas