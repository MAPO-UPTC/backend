# 🌐 Integración Frontend-Backend: Sistema de Roles

## 📋 Información para el Frontend

### 🔗 Endpoints Disponibles

```typescript
// Base URL de tu API
const API_BASE_URL = "http://localhost:8000";

// Endpoints de autenticación
POST /users/signup        // Registro de usuario
POST /users/login         // Login (devuelve idToken y permisos)
POST /users/ping          // Validar token

// Endpoints de permisos y roles
GET  /users/me/permissions    // Obtener permisos actuales
GET  /users/me/profile       // Perfil completo del usuario
POST /users/me/switch-role   // Cambiar rol activo
POST /users/me/clear-active-role // Limpiar rol activo
GET  /users/me/active-role   // Ver rol activo

// Endpoints protegidos (ejemplos)
GET  /products/             // Leer productos (requiere permiso READ)
POST /products/             // Crear producto (requiere permiso CREATE)
PUT  /products/{id}         // Actualizar producto (requiere permiso UPDATE)
DELETE /products/{id}       // Eliminar producto (requiere permiso DELETE)
```

### 🎭 Tipos y Interfaces TypeScript

```typescript
// types/auth.ts
export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignUpRequest {
  email: string;
  password: string;
  name: string;
  last_name: string;
  document_type: string;
  document_number: string;
}

export interface LoginResponse {
  message: string;
  idToken: string;
  user: UserWithPermissions;
}

export interface UserWithPermissions {
  id: string;
  email: string;
  name: string;
  last_name: string;
  document_type: string;
  document_number: string;
  roles: Role[];
  permissions: PermissionMatrix;
}

export interface PermissionResponse {
  user_id: string;
  available_roles: Role[];
  active_role: Role | null;
  effective_roles: Role[];
  permissions: PermissionMatrix;
}

export interface SwitchRoleRequest {
  role: Role;
}

export interface ActiveRoleResponse {
  active_role: Role | null;
  available_roles: Role[];
  permissions: PermissionMatrix;
}

// Enums de roles
export enum Role {
  USER = "USER",
  ADMIN = "ADMIN",
  SUPERADMIN = "SUPERADMIN"
}

// Enums de entidades
export enum Entity {
  USERS = "USERS",
  PRODUCTS = "PRODUCTS",
  SUPPLIERS = "SUPPLIERS",
  CLIENTS = "CLIENTS",
  SALES_ORDERS = "SALES_ORDERS",
  INVENTORY_STOCK = "INVENTORY_STOCK"
}

// Enums de acciones
export enum Action {
  CREATE = "CREATE",
  READ = "READ",
  UPDATE = "UPDATE",
  DELETE = "DELETE"
}

// Enums de niveles de permisos
export enum PermissionLevel {
  NONE = "NONE",
  OWN = "OWN",
  CONDITIONAL = "CONDITIONAL",
  ALL = "ALL"
}

// Matriz de permisos
export type PermissionMatrix = {
  [entity in Entity]?: {
    [action in Action]?: PermissionLevel;
  };
};
```

### 🔧 Cliente HTTP con Interceptores

```typescript
// api/client.ts
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para agregar token automáticamente
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Interceptor para manejar errores de autenticación
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.clearToken();
          // Redirigir a login o mostrar modal
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  loadToken() {
    const token = localStorage.getItem('auth_token');
    if (token) {
      this.token = token;
    }
  }

  // Métodos HTTP
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete(url, config);
    return response.data;
  }
}

export const apiClient = new ApiClient('http://localhost:8000');
```

### 🔐 Servicio de Autenticación

```typescript
// services/authService.ts
import { apiClient } from '../api/client';
import { 
  LoginRequest, 
  LoginResponse, 
  SignUpRequest, 
  PermissionResponse,
  SwitchRoleRequest,
  ActiveRoleResponse,
  Role 
} from '../types/auth';

export class AuthService {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/users/login', credentials);
    
    // Guardar token automáticamente
    apiClient.setToken(response.idToken);
    
    return response;
  }

  async signup(userData: SignUpRequest): Promise<any> {
    return apiClient.post('/users/signup', userData);
  }

  async getPermissions(): Promise<PermissionResponse> {
    return apiClient.get<PermissionResponse>('/users/me/permissions');
  }

  async switchRole(role: Role): Promise<ActiveRoleResponse> {
    return apiClient.post<ActiveRoleResponse>('/users/me/switch-role', { role });
  }

  async clearActiveRole(): Promise<any> {
    return apiClient.post('/users/me/clear-active-role');
  }

  async getActiveRole(): Promise<ActiveRoleResponse> {
    return apiClient.get<ActiveRoleResponse>('/users/me/active-role');
  }

  async validateToken(): Promise<any> {
    return apiClient.post('/users/ping');
  }

  logout() {
    apiClient.clearToken();
    // Limpiar cualquier estado adicional
  }
}

export const authService = new AuthService();
```

### 🎯 Hook de React para Roles

```typescript
// hooks/useRoleSwitching.ts
import { useState, useEffect, useCallback } from 'react';
import { authService } from '../services/authService';
import { PermissionResponse, Role, Entity, Action, PermissionLevel } from '../types/auth';

export const useRoleSwitching = () => {
  const [permissions, setPermissions] = useState<PermissionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cargar permisos iniciales
  const loadPermissions = useCallback(async () => {
    try {
      setLoading(true);
      const perms = await authService.getPermissions();
      setPermissions(perms);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Error loading permissions');
    } finally {
      setLoading(false);
    }
  }, []);

  // Cambiar rol activo
  const switchRole = useCallback(async (role: Role) => {
    try {
      setLoading(true);
      const result = await authService.switchRole(role);
      
      // Actualizar permisos locales
      setPermissions(prev => prev ? {
        ...prev,
        active_role: result.active_role,
        effective_roles: [role],
        permissions: result.permissions
      } : null);
      
      setError(null);
      return result;
    } catch (err: any) {
      setError(err.message || 'Error switching role');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Limpiar rol activo
  const clearActiveRole = useCallback(async () => {
    try {
      setLoading(true);
      await authService.clearActiveRole();
      await loadPermissions(); // Recargar permisos completos
    } catch (err: any) {
      setError(err.message || 'Error clearing active role');
    } finally {
      setLoading(false);
    }
  }, [loadPermissions]);

  // Verificar si tiene un permiso específico
  const hasPermission = useCallback((entity: Entity, action: Action, level: PermissionLevel = PermissionLevel.ALL): boolean => {
    if (!permissions?.permissions[entity]) return false;
    
    const userLevel = permissions.permissions[entity][action];
    if (!userLevel || userLevel === PermissionLevel.NONE) return false;
    
    // Jerarquía: ALL > CONDITIONAL > OWN > NONE
    const hierarchy = {
      [PermissionLevel.ALL]: 4,
      [PermissionLevel.CONDITIONAL]: 3,
      [PermissionLevel.OWN]: 2,
      [PermissionLevel.NONE]: 1
    };
    
    return hierarchy[userLevel] >= hierarchy[level];
  }, [permissions]);

  // Verificar si puede realizar una acción específica
  const canCreate = useCallback((entity: Entity) => hasPermission(entity, Action.CREATE), [hasPermission]);
  const canRead = useCallback((entity: Entity) => hasPermission(entity, Action.READ), [hasPermission]);
  const canUpdate = useCallback((entity: Entity) => hasPermission(entity, Action.UPDATE), [hasPermission]);
  const canDelete = useCallback((entity: Entity) => hasPermission(entity, Action.DELETE), [hasPermission]);

  useEffect(() => {
    loadPermissions();
  }, [loadPermissions]);

  return {
    permissions,
    loading,
    error,
    switchRole,
    clearActiveRole,
    loadPermissions,
    hasPermission,
    canCreate,
    canRead,
    canUpdate,
    canDelete,
    // Propiedades de conveniencia
    availableRoles: permissions?.available_roles || [],
    activeRole: permissions?.active_role,
    effectiveRoles: permissions?.effective_roles || [],
    hasMultipleRoles: (permissions?.available_roles.length || 0) > 1
  };
};
```

### 🎨 Componentes de UI

```typescript
// components/RoleSelector.tsx
import React from 'react';
import { Role } from '../types/auth';

interface RoleSelectorProps {
  availableRoles: Role[];
  activeRole: Role | null;
  onRoleChange: (role: Role) => void;
  onClearRole: () => void;
  loading?: boolean;
}

export const RoleSelector: React.FC<RoleSelectorProps> = ({
  availableRoles,
  activeRole,
  onRoleChange,
  onClearRole,
  loading = false
}) => {
  if (availableRoles.length <= 1) return null;

  return (
    <div className="role-selector">
      <label htmlFor="role-select">Rol Activo:</label>
      <select
        id="role-select"
        value={activeRole || ''}
        onChange={(e) => {
          if (e.target.value === '') {
            onClearRole();
          } else {
            onRoleChange(e.target.value as Role);
          }
        }}
        disabled={loading}
      >
        <option value="">Todos los roles</option>
        {availableRoles.map(role => (
          <option key={role} value={role}>
            {role}
          </option>
        ))}
      </select>
      
      {activeRole && (
        <div className="active-role-indicator">
          🎭 Usando rol: <strong>{activeRole}</strong>
        </div>
      )}
    </div>
  );
};
```

```typescript
// components/ProtectedComponent.tsx
import React from 'react';
import { useRoleSwitching } from '../hooks/useRoleSwitching';
import { Entity, Action, PermissionLevel } from '../types/auth';

interface ProtectedComponentProps {
  entity: Entity;
  action: Action;
  level?: PermissionLevel;
  fallback?: React.ReactNode;
  children: React.ReactNode;
}

export const ProtectedComponent: React.FC<ProtectedComponentProps> = ({
  entity,
  action,
  level = PermissionLevel.ALL,
  fallback = null,
  children
}) => {
  const { hasPermission, loading } = useRoleSwitching();

  if (loading) return <div>Cargando...</div>;

  if (!hasPermission(entity, action, level)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};
```

### 📱 Ejemplo de Componente de Productos

```typescript
// components/ProductList.tsx
import React from 'react';
import { useRoleSwitching } from '../hooks/useRoleSwitching';
import { ProtectedComponent } from './ProtectedComponent';
import { RoleSelector } from './RoleSelector';
import { Entity, Action } from '../types/auth';

export const ProductList: React.FC = () => {
  const {
    permissions,
    switchRole,
    clearActiveRole,
    canCreate,
    canUpdate,
    canDelete,
    availableRoles,
    activeRole,
    hasMultipleRoles,
    loading
  } = useRoleSwitching();

  const handleCreateProduct = () => {
    // Lógica para crear producto
    console.log('Creating product...');
  };

  const handleUpdateProduct = (id: string) => {
    // Lógica para actualizar producto
    console.log('Updating product:', id);
  };

  const handleDeleteProduct = (id: string) => {
    // Lógica para eliminar producto
    console.log('Deleting product:', id);
  };

  if (loading) return <div>Cargando permisos...</div>;

  return (
    <div className="product-list">
      <h2>Lista de Productos</h2>
      
      {/* Selector de roles si tiene múltiples */}
      {hasMultipleRoles && (
        <RoleSelector
          availableRoles={availableRoles}
          activeRole={activeRole}
          onRoleChange={switchRole}
          onClearRole={clearActiveRole}
          loading={loading}
        />
      )}

      {/* Botón crear - solo si tiene permisos */}
      <ProtectedComponent
        entity={Entity.PRODUCTS}
        action={Action.CREATE}
        fallback={<p>No tienes permisos para crear productos</p>}
      >
        <button onClick={handleCreateProduct}>
          ➕ Crear Producto
        </button>
      </ProtectedComponent>

      {/* Lista de productos */}
      <div className="products">
        {/* Ejemplo de productos */}
        <div className="product-item">
          <h4>Producto 1</h4>
          <p>Descripción del producto</p>
          
          <div className="product-actions">
            {/* Botón editar */}
            {canUpdate(Entity.PRODUCTS) && (
              <button onClick={() => handleUpdateProduct('1')}>
                ✏️ Editar
              </button>
            )}
            
            {/* Botón eliminar */}
            {canDelete(Entity.PRODUCTS) && (
              <button onClick={() => handleDeleteProduct('1')}>
                🗑️ Eliminar
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Debug: Mostrar permisos actuales */}
      {process.env.NODE_ENV === 'development' && (
        <details className="debug-permissions">
          <summary>🔍 Debug: Permisos actuales</summary>
          <pre>{JSON.stringify(permissions, null, 2)}</pre>
        </details>
      )}
    </div>
  );
};
```

### 🚀 Configuración inicial

```typescript
// App.tsx
import React, { useEffect } from 'react';
import { apiClient } from './api/client';
import { ProductList } from './components/ProductList';

function App() {
  useEffect(() => {
    // Cargar token del localStorage al iniciar la app
    apiClient.loadToken();
  }, []);

  return (
    <div className="App">
      <ProductList />
    </div>
  );
}

export default App;
```

## 📦 Archivos para compartir

Crea estos archivos en la carpeta de tu frontend y compártelos con tu equipo:

1. `types/auth.ts` - Tipos TypeScript
2. `api/client.ts` - Cliente HTTP
3. `services/authService.ts` - Servicio de autenticación
4. `hooks/useRoleSwitching.ts` - Hook de React
5. `components/RoleSelector.tsx` - Selector de roles
6. `components/ProtectedComponent.tsx` - Componente protegido

## 🎯 Pasos para implementar en el frontend:

1. **Instalar dependencias:**
```bash
npm install axios
npm install @types/node  # Si usas TypeScript
```

2. **Copiar los archivos de tipos e interfaces**

3. **Configurar el cliente HTTP con tu URL de backend**

4. **Implementar el hook `useRoleSwitching`**

5. **Usar `ProtectedComponent` para mostrar/ocultar elementos**

6. **Agregar `RoleSelector` donde sea necesario**

¡Con esto tu frontend tendrá todo el contexto necesario para implementar el sistema de roles! 🚀