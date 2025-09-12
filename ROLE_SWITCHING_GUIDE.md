# 🎭 Sistema de Cambio de Roles - Guía de Uso

## 📋 Descripción General

El sistema de cambio de roles permite que un usuario con múltiples roles asignados pueda **elegir activamente** qué rol usar en un momento específico. Esto es útil para:

- **Seguridad**: Evitar usar permisos altos innecesariamente
- **UX/UI**: Mostrar diferentes interfaces según el rol activo
- **Auditoría**: Saber exactamente con qué rol se realizó cada acción
- **Flexibilidad**: Alternar entre diferentes niveles de permisos

## 🔧 Funcionamiento Técnico

### Estados del Usuario

1. **Sin rol activo** (por defecto): Usa todos los roles asignados con permisos combinados (siempre toma el más alto)
2. **Con rol activo**: Usa únicamente los permisos del rol seleccionado

### Endpoints Disponibles

#### 1. Ver permisos actuales
```http
GET /users/me/permissions
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "user_id": "uuid",
  "available_roles": ["USER", "ADMIN", "SUPERADMIN"],
  "active_role": null,  // o "USER", "ADMIN", etc.
  "effective_roles": ["USER", "ADMIN", "SUPERADMIN"],  // roles que se están usando
  "permissions": {
    "PRODUCTS": {
      "READ": "ALL",
      "CREATE": "ALL"
    }
  }
}
```

#### 2. Cambiar a un rol específico
```http
POST /users/me/switch-role
Authorization: Bearer {token}
Content-Type: application/json
```

**Body:**
```json
{
  "role": "USER"  // USER, ADMIN, o SUPERADMIN
}
```

**Respuesta:**
```json
{
  "active_role": "USER",
  "available_roles": ["USER", "ADMIN", "SUPERADMIN"],
  "permissions": {
    "PRODUCTS": {
      "READ": "ALL",
      "CREATE": "NONE"
    }
  }
}
```

#### 3. Limpiar rol activo (volver a usar todos)
```http
POST /users/me/clear-active-role
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "message": "Active role cleared. Now using all assigned roles.",
  "available_roles": ["USER", "ADMIN", "SUPERADMIN"]
}
```

#### 4. Ver rol activo actual
```http
GET /users/me/active-role
Authorization: Bearer {token}
```

## 🎯 Casos de Uso Prácticos

### Caso 1: Usuario con múltiples roles
```
Usuario tiene: [USER, ADMIN, SUPERADMIN]

1. Sin rol activo: Puede hacer TODO (permisos de SUPERADMIN)
2. Activa rol USER: Solo puede leer productos, no crear
3. Activa rol ADMIN: Puede crear/editar productos, no eliminar usuarios
4. Activa rol SUPERADMIN: Puede hacer TODO
5. Limpia rol activo: Vuelve a poder hacer TODO
```

### Caso 2: Frontend dinámico
```javascript
// Al iniciar sesión
const permissions = await fetch('/users/me/permissions');
const { available_roles, active_role, permissions: perms } = await permissions.json();

// Mostrar selector de roles si tiene múltiples
if (available_roles.length > 1) {
  showRoleSelector(available_roles, active_role);
}

// Cambiar rol
async function switchRole(newRole) {
  const response = await fetch('/users/me/switch-role', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role: newRole })
  });
  
  const result = await response.json();
  updateUIBasedOnPermissions(result.permissions);
}
```

### Caso 3: Auditoría de acciones
```
LOG: Usuario Juan (active_role: USER) intentó crear producto → DENEGADO
LOG: Usuario Juan cambió a rol ADMIN
LOG: Usuario Juan (active_role: ADMIN) creó producto "Laptop Dell" → PERMITIDO
```

## ⚡ Ejemplos de Flujo de Trabajo

### Flujo 1: Administrador usando rol restringido
```bash
# 1. Login como admin con múltiples roles
POST /users/login → roles: [USER, ADMIN]

# 2. Por defecto usa todos los roles (permisos máximos)
GET /users/me/permissions → effective_roles: [USER, ADMIN]

# 3. Cambia a rol USER para trabajo día a día (más seguro)
POST /users/me/switch-role {"role": "USER"}

# 4. Ahora solo tiene permisos de USER
GET /products/ → ✅ Permitido (lectura)
POST /products/ → ❌ Denegado (no puede crear)

# 5. Necesita crear un producto, cambia a ADMIN
POST /users/me/switch-role {"role": "ADMIN"}
POST /products/ → ✅ Permitido (puede crear)

# 6. Termina la tarea, vuelve a USER
POST /users/me/switch-role {"role": "USER"}
```

### Flujo 2: Superadmin temporal
```bash
# 1. Usuario con [USER, SUPERADMIN]
GET /users/me/permissions → effective_roles: [USER, SUPERADMIN]

# 2. Usa solo USER para tareas normales
POST /users/me/switch-role {"role": "USER"}

# 3. Necesita eliminar algo crítico
POST /users/me/switch-role {"role": "SUPERADMIN"}
DELETE /products/123 → ✅ Permitido

# 4. Inmediatamente vuelve a USER
POST /users/me/switch-role {"role": "USER"}
```

## 🛡️ Consideraciones de Seguridad

1. **Validación**: Solo se puede cambiar a roles que realmente tiene asignados
2. **Temporalidad**: El rol activo se mantiene en memoria (se pierde al reiniciar servidor)
3. **Auditoría**: Todas las acciones registran qué rol estaba activo
4. **Tokens**: El rol activo no modifica el token JWT, es adicional

## 🔄 Persistencia y Limitaciones

### En Memoria vs Base de Datos
- **Actual**: Roles activos se guardan en memoria (se pierden al reiniciar)
- **Producción**: Considerar usar Redis o tabla de sesiones para persistencia

### Limitaciones
- Un usuario puede tener solo UN rol activo a la vez
- Si el rol activo no está en sus roles asignados, se ignora
- Los permisos se calculan en tiempo real

## 📱 Integración con Frontend

### React/Vue/Angular
```typescript
interface UserPermissions {
  user_id: string;
  available_roles: string[];
  active_role: string | null;
  effective_roles: string[];
  permissions: Record<string, Record<string, string>>;
}

// Hook para manejar roles
const useRoleSwitching = () => {
  const [userPermissions, setUserPermissions] = useState<UserPermissions>();
  
  const switchRole = async (role: string) => {
    const response = await api.post('/users/me/switch-role', { role });
    setUserPermissions(response.data);
  };
  
  const clearActiveRole = async () => {
    await api.post('/users/me/clear-active-role');
    // Refrescar permisos
  };
  
  return { userPermissions, switchRole, clearActiveRole };
};
```

### Mostrar/Ocultar elementos según permisos
```jsx
const ProductActions = ({ userPermissions }) => {
  const canCreate = userPermissions.permissions.PRODUCTS?.CREATE !== 'NONE';
  const canDelete = userPermissions.permissions.PRODUCTS?.DELETE !== 'NONE';
  
  return (
    <div>
      {canCreate && <button>Crear Producto</button>}
      {canDelete && <button>Eliminar</button>}
      
      {/* Selector de roles si tiene múltiples */}
      {userPermissions.available_roles.length > 1 && (
        <RoleSelector 
          roles={userPermissions.available_roles}
          activeRole={userPermissions.active_role}
          onRoleChange={switchRole}
        />
      )}
    </div>
  );
};
```

## ✅ Pruebas y Validación

El sistema incluye un script de pruebas completo: `test_role_switching.py`

```bash
# Ejecutar pruebas
python test_role_switching.py
```

**Valida:**
- ✅ Login y obtención de permisos
- ✅ Cambio de roles entre disponibles
- ✅ Restricciones de permisos según rol activo
- ✅ Limpieza de rol activo
- ✅ Mensajes de error apropiados
- ✅ Combinación de permisos sin rol activo

---

## 🎉 Conclusión

Este sistema te permite implementar un control de acceso granular y dinámico donde los usuarios pueden **elegir el nivel de permisos** que quieren usar en cada momento, mejorando tanto la seguridad como la experiencia de usuario.