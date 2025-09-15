# 🔥 Ejemplos Prácticos de Peticiones HTTP

## 📝 Colección para Postman/Insomnia

```json
{
  "name": "MAPO Backend - Role System",
  "requests": [
    {
      "name": "1. Registro de Usuario",
      "method": "POST",
      "url": "http://localhost:8000/users/signup",
      "headers": {
        "Content-Type": "application/json"
      },
      "body": {
        "email": "juan@example.com",
        "password": "password123",
        "name": "Juan",
        "last_name": "Pérez",
        "document_type": "CC",
        "document_number": "12345678"
      }
    },
    {
      "name": "2. Login",
      "method": "POST",
      "url": "http://localhost:8000/users/login",
      "headers": {
        "Content-Type": "application/json"
      },
      "body": {
        "email": "juan@example.com",
        "password": "password123"
      }
    },
    {
      "name": "3. Ver Permisos Actuales",
      "method": "GET",
      "url": "http://localhost:8000/users/me/permissions",
      "headers": {
        "Authorization": "Bearer {{idToken}}"
      }
    },
    {
      "name": "4. Cambiar a Rol USER",
      "method": "POST",
      "url": "http://localhost:8000/users/me/switch-role",
      "headers": {
        "Authorization": "Bearer {{idToken}}",
        "Content-Type": "application/json"
      },
      "body": {
        "role": "USER"
      }
    },
    {
      "name": "5. Cambiar a Rol ADMIN",
      "method": "POST",
      "url": "http://localhost:8000/users/me/switch-role",
      "headers": {
        "Authorization": "Bearer {{idToken}}",
        "Content-Type": "application/json"
      },
      "body": {
        "role": "ADMIN"
      }
    },
    {
      "name": "6. Limpiar Rol Activo",
      "method": "POST",
      "url": "http://localhost:8000/users/me/clear-active-role",
      "headers": {
        "Authorization": "Bearer {{idToken}}"
      }
    },
    {
      "name": "7. Leer Productos (Permitido para USER)",
      "method": "GET",
      "url": "http://localhost:8000/products/",
      "headers": {
        "Authorization": "Bearer {{idToken}}"
      }
    },
    {
      "name": "8. Crear Producto (Requiere ADMIN+)",
      "method": "POST",
      "url": "http://localhost:8000/products/",
      "headers": {
        "Authorization": "Bearer {{idToken}}",
        "Content-Type": "application/json"
      },
      "body": {
        "name": "Nuevo Producto",
        "description": "Descripción del producto",
        "price": 100.0,
        "stock": 50
      }
    }
  ]
}
```

## 🌐 Ejemplos con JavaScript/Fetch

### 1. Login y manejo de token

```javascript
// Login
async function login(email, password) {
  try {
    const response = await fetch('http://localhost:8000/users/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // Guardar token en localStorage
    localStorage.setItem('authToken', data.idToken);
    
    console.log('Login exitoso:', data.user);
    return data;
  } catch (error) {
    console.error('Error en login:', error);
    throw error;
  }
}

// Usar el login
login('test@example.com', 'password123')
  .then(data => {
    console.log('Usuario logueado:', data.user.email);
    console.log('Roles disponibles:', data.user.roles);
  });
```

### 2. Función helper para peticiones autenticadas

```javascript
// Helper para peticiones autenticadas
async function authenticatedFetch(url, options = {}) {
  const token = localStorage.getItem('authToken');
  
  if (!token) {
    throw new Error('No authentication token found');
  }

  const defaultHeaders = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers
    }
  };

  const response = await fetch(url, config);

  if (response.status === 401) {
    // Token expirado o inválido
    localStorage.removeItem('authToken');
    window.location.href = '/login';
    throw new Error('Authentication failed');
  }

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}
```

### 3. Gestión de permisos

```javascript
// Obtener permisos actuales
async function getCurrentPermissions() {
  try {
    const permissions = await authenticatedFetch('http://localhost:8000/users/me/permissions');
    console.log('Permisos actuales:', permissions);
    return permissions;
  } catch (error) {
    console.error('Error obteniendo permisos:', error);
    throw error;
  }
}

// Cambiar rol activo
async function switchToRole(role) {
  try {
    const result = await authenticatedFetch('http://localhost:8000/users/me/switch-role', {
      method: 'POST',
      body: JSON.stringify({ role })
    });
    
    console.log(`Cambiado a rol ${role}:`, result);
    return result;
  } catch (error) {
    console.error(`Error cambiando a rol ${role}:`, error);
    throw error;
  }
}

// Limpiar rol activo
async function clearActiveRole() {
  try {
    const result = await authenticatedFetch('http://localhost:8000/users/me/clear-active-role', {
      method: 'POST'
    });
    
    console.log('Rol activo limpiado:', result);
    return result;
  } catch (error) {
    console.error('Error limpiando rol activo:', error);
    throw error;
  }
}
```

### 4. Verificación de permisos

```javascript
// Clase para manejar permisos
class PermissionManager {
  constructor(permissions) {
    this.permissions = permissions;
  }

  // Verificar si tiene un permiso específico
  hasPermission(entity, action, level = 'ALL') {
    const entityPerms = this.permissions[entity];
    if (!entityPerms) return false;

    const userLevel = entityPerms[action];
    if (!userLevel || userLevel === 'NONE') return false;

    // Jerarquía de permisos
    const hierarchy = { 'ALL': 4, 'CONDITIONAL': 3, 'OWN': 2, 'NONE': 1 };
    return hierarchy[userLevel] >= hierarchy[level];
  }

  // Métodos de conveniencia
  canCreate(entity) { return this.hasPermission(entity, 'CREATE'); }
  canRead(entity) { return this.hasPermission(entity, 'READ'); }
  canUpdate(entity) { return this.hasPermission(entity, 'UPDATE'); }
  canDelete(entity) { return this.hasPermission(entity, 'DELETE'); }
}

// Ejemplo de uso
async function checkProductPermissions() {
  const perms = await getCurrentPermissions();
  const permManager = new PermissionManager(perms.permissions);

  console.log('¿Puede crear productos?', permManager.canCreate('PRODUCTS'));
  console.log('¿Puede leer productos?', permManager.canRead('PRODUCTS'));
  console.log('¿Puede actualizar productos?', permManager.canUpdate('PRODUCTS'));
  console.log('¿Puede eliminar productos?', permManager.canDelete('PRODUCTS'));
}
```

### 5. Flujo completo de cambio de roles

```javascript
// Demostración completa del sistema de roles
async function demonstrateRoleSwitching() {
  try {
    console.log('=== DEMOSTRACIÓN SISTEMA DE ROLES ===');

    // 1. Obtener permisos iniciales
    console.log('\n1. Permisos iniciales:');
    let permissions = await getCurrentPermissions();
    console.log('Roles disponibles:', permissions.available_roles);
    console.log('Rol activo:', permissions.active_role || 'Ninguno (todos los roles)');

    // 2. Probar acceso a productos con todos los roles
    console.log('\n2. Intentando leer productos (todos los roles):');
    try {
      const products = await authenticatedFetch('http://localhost:8000/products/');
      console.log('✅ Lectura exitosa:', products.length, 'productos');
    } catch (error) {
      console.log('❌ Error:', error.message);
    }

    // 3. Cambiar a rol USER
    if (permissions.available_roles.includes('USER')) {
      console.log('\n3. Cambiando a rol USER:');
      await switchToRole('USER');

      // Probar crear producto (debería fallar)
      console.log('Intentando crear producto con rol USER:');
      try {
        await authenticatedFetch('http://localhost:8000/products/', {
          method: 'POST',
          body: JSON.stringify({
            name: 'Producto de prueba',
            description: 'Descripción de prueba'
          })
        });
        console.log('✅ Creación exitosa');
      } catch (error) {
        console.log('❌ Error esperado:', error.message);
      }
    }

    // 4. Cambiar a rol ADMIN
    if (permissions.available_roles.includes('ADMIN')) {
      console.log('\n4. Cambiando a rol ADMIN:');
      await switchToRole('ADMIN');

      // Probar crear producto (debería funcionar)
      console.log('Intentando crear producto con rol ADMIN:');
      try {
        const newProduct = await authenticatedFetch('http://localhost:8000/products/', {
          method: 'POST',
          body: JSON.stringify({
            name: 'Producto Admin ' + Date.now(),
            description: 'Producto creado por admin'
          })
        });
        console.log('✅ Producto creado:', newProduct);
      } catch (error) {
        console.log('❌ Error:', error.message);
      }
    }

    // 5. Limpiar rol activo
    console.log('\n5. Limpiando rol activo:');
    await clearActiveRole();

    // 6. Verificar permisos finales
    console.log('\n6. Permisos finales:');
    permissions = await getCurrentPermissions();
    console.log('Rol activo:', permissions.active_role || 'Ninguno (todos los roles)');
    console.log('Roles efectivos:', permissions.effective_roles);

  } catch (error) {
    console.error('Error en demostración:', error);
  }
}

// Ejecutar demostración
// demonstrateRoleSwitching();
```

## 🎨 Ejemplo con React Hooks

```javascript
// Hook personalizado para manejar autenticación y roles
import { useState, useEffect, useCallback } from 'react';

export function useAuth() {
  const [user, setUser] = useState(null);
  const [permissions, setPermissions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Login
  const login = useCallback(async (email, password) => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/users/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) throw new Error('Login failed');

      const data = await response.json();
      localStorage.setItem('authToken', data.idToken);
      setUser(data.user);
      setError(null);
      
      // Cargar permisos
      await loadPermissions();
      
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Cargar permisos
  const loadPermissions = useCallback(async () => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) return;

      const response = await fetch('http://localhost:8000/users/me/permissions', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to load permissions');

      const perms = await response.json();
      setPermissions(perms);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  // Cambiar rol
  const switchRole = useCallback(async (role) => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch('http://localhost:8000/users/me/switch-role', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ role })
      });

      if (!response.ok) throw new Error('Failed to switch role');

      await loadPermissions(); // Recargar permisos
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [loadPermissions]);

  // Logout
  const logout = useCallback(() => {
    localStorage.removeItem('authToken');
    setUser(null);
    setPermissions(null);
  }, []);

  // Verificar permisos
  const hasPermission = useCallback((entity, action) => {
    if (!permissions?.permissions[entity]) return false;
    const level = permissions.permissions[entity][action];
    return level && level !== 'NONE';
  }, [permissions]);

  // Cargar datos iniciales
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      loadPermissions();
    } else {
      setLoading(false);
    }
  }, [loadPermissions]);

  return {
    user,
    permissions,
    loading,
    error,
    login,
    logout,
    switchRole,
    hasPermission,
    isAuthenticated: !!user,
    availableRoles: permissions?.available_roles || [],
    activeRole: permissions?.active_role
  };
}
```

## 📋 Checklist para el Frontend

- [ ] Instalar dependencias (axios o fetch nativo)
- [ ] Copiar tipos TypeScript si aplica
- [ ] Configurar cliente HTTP con interceptores
- [ ] Implementar servicio de autenticación
- [ ] Crear hook o servicio para manejo de roles
- [ ] Implementar componentes protegidos
- [ ] Agregar selector de roles en la UI
- [ ] Manejar errores 401/403 apropiadamente
- [ ] Probar flujo completo de cambio de roles
- [ ] Implementar persistencia de token en localStorage

¡Con estos ejemplos tu equipo de frontend puede implementar todo el sistema de roles! 🚀