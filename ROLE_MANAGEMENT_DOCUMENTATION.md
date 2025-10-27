# Sistema de Gestión de Roles y Permisos

## Descripción General

Sistema completo para que usuarios con rol **SUPERADMIN** puedan gestionar roles de otros usuarios del sistema. Permite asignar, remover y consultar roles de forma segura y controlada.

## Características Principales

### 🔐 Seguridad
- **Solo SUPERADMIN**: Todos los endpoints requieren rol SUPERADMIN
- **Protección del último SUPERADMIN**: No se puede remover el rol SUPERADMIN si es el único en el sistema
- **Validación de roles**: Solo se pueden asignar roles válidos (USER, ADMIN, SUPERADMIN)
- **Mínimo un rol**: Los usuarios siempre deben tener al menos un rol asignado

### 📊 Funcionalidades
1. **Listar usuarios con roles** - Ver todos los usuarios y sus roles asignados
2. **Ver roles de un usuario** - Consultar roles de un usuario específico
3. **Asignar rol** - Agregar un rol a un usuario
4. **Remover rol** - Quitar un rol de un usuario
5. **Actualizar roles** - Reemplazar todos los roles de un usuario
6. **Roles disponibles** - Consultar lista de roles del sistema

## Endpoints Disponibles

### 1. GET `/role-management/users`
Obtener todos los usuarios con sus roles asignados.

**Requiere:** SUPERADMIN

**Respuesta:**
```json
{
  "users": [
    {
      "user_id": "uuid",
      "email": "user@example.com",
      "name": "Juan",
      "last_name": "Pérez",
      "document_type": "CC",
      "document_number": "1234567890",
      "roles": ["USER", "ADMIN"]
    }
  ],
  "total": 10
}
```

**Ejemplo cURL:**
```bash
curl -X GET "http://localhost:8000/role-management/users" \
  -H "Authorization: Bearer YOUR_SUPERADMIN_TOKEN"
```

---

### 2. GET `/role-management/users/{user_id}`
Obtener roles de un usuario específico.

**Requiere:** SUPERADMIN

**Parámetros:**
- `user_id` (path): UUID del usuario

**Respuesta:**
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "name": "Juan",
  "last_name": "Pérez",
  "document_type": "CC",
  "document_number": "1234567890",
  "roles": ["USER", "ADMIN"]
}
```

**Ejemplo cURL:**
```bash
curl -X GET "http://localhost:8000/role-management/users/{user_id}" \
  -H "Authorization: Bearer YOUR_SUPERADMIN_TOKEN"
```

---

### 3. POST `/role-management/assign-role`
Asignar un rol a un usuario.

**Requiere:** SUPERADMIN

**Request Body:**
```json
{
  "user_id": "uuid-del-usuario",
  "role": "ADMIN"
}
```

**Roles disponibles:**
- `USER`: Usuario básico (permisos limitados)
- `ADMIN`: Administrador (permisos amplios)
- `SUPERADMIN`: Super administrador (todos los permisos)

**Validaciones:**
- ✅ El usuario debe existir
- ✅ El rol debe ser válido
- ✅ El usuario no debe tener ya ese rol

**Respuesta exitosa:**
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "name": "Juan",
  "last_name": "Pérez",
  "roles": ["USER", "ADMIN"],
  "message": "Rol ADMIN asignado exitosamente"
}
```

**Ejemplo cURL:**
```bash
curl -X POST "http://localhost:8000/role-management/assign-role" \
  -H "Authorization: Bearer YOUR_SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "role": "ADMIN"
  }'
```

---

### 4. POST `/role-management/remove-role`
Remover un rol de un usuario.

**Requiere:** SUPERADMIN

**Request Body:**
```json
{
  "user_id": "uuid-del-usuario",
  "role": "ADMIN"
}
```

**Validaciones:**
- ✅ El usuario debe existir
- ✅ El usuario debe tener el rol asignado
- ✅ El usuario no puede quedar sin roles (mínimo 1)
- ✅ No se puede remover SUPERADMIN si es el único SUPERADMIN

**Protecciones:**
- 🛡️ Siempre debe haber al menos un SUPERADMIN en el sistema
- 🛡️ Un usuario siempre debe tener al menos un rol

**Respuesta exitosa:**
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "name": "Juan",
  "last_name": "Pérez",
  "roles": ["USER"],
  "message": "Rol ADMIN removido exitosamente"
}
```

**Ejemplo cURL:**
```bash
curl -X POST "http://localhost:8000/role-management/remove-role" \
  -H "Authorization: Bearer YOUR_SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "role": "ADMIN"
  }'
```

---

### 5. PUT `/role-management/users/{user_id}/roles`
Actualizar todos los roles de un usuario (reemplaza roles existentes).

**Requiere:** SUPERADMIN

**Parámetros:**
- `user_id` (path): UUID del usuario

**Request Body:**
```json
["USER", "ADMIN"]
```

**⚠️ IMPORTANTE:** Esta operación **reemplaza TODOS** los roles actuales del usuario.

**Validaciones:**
- ✅ El usuario debe existir
- ✅ Debe proporcionar al menos un rol
- ✅ Todos los roles deben ser válidos

**Respuesta exitosa:**
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "name": "Juan",
  "last_name": "Pérez",
  "roles": ["USER", "ADMIN"],
  "message": "Roles actualizados exitosamente"
}
```

**Ejemplo cURL:**
```bash
curl -X PUT "http://localhost:8000/role-management/users/{user_id}/roles" \
  -H "Authorization: Bearer YOUR_SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '["USER", "ADMIN"]'
```

---

### 6. GET `/role-management/available-roles`
Obtener lista de roles disponibles en el sistema.

**Requiere:** SUPERADMIN

**Respuesta:**
```json
{
  "roles": [
    {
      "name": "USER",
      "description": "Usuario básico con permisos limitados. Puede ver productos, crear clientes y ver sus propias ventas."
    },
    {
      "name": "ADMIN",
      "description": "Administrador con permisos amplios. Puede gestionar productos, proveedores, inventario y todas las ventas."
    },
    {
      "name": "SUPERADMIN",
      "description": "Super administrador con todos los permisos. Puede gestionar usuarios, roles y tiene acceso completo al sistema."
    }
  ]
}
```

**Ejemplo cURL:**
```bash
curl -X GET "http://localhost:8000/role-management/available-roles" \
  -H "Authorization: Bearer YOUR_SUPERADMIN_TOKEN"
```

---

### 7. GET `/role-management/my-permissions`
Obtener información detallada de los permisos del SUPERADMIN actual.

**Requiere:** SUPERADMIN

**Respuesta:**
```json
{
  "user_id": "uuid",
  "email": "superadmin@example.com",
  "roles": ["SUPERADMIN"],
  "active_role": "SUPERADMIN",
  "permissions": {
    "USERS": {
      "CREATE": "ALL",
      "READ": "ALL",
      "UPDATE": "ALL",
      "DELETE": "ALL"
    },
    "PRODUCTS": { ... }
  }
}
```

## Roles del Sistema

### USER
**Permisos:**
- ✅ Puede ver productos
- ✅ Puede crear y ver clientes
- ✅ Puede ver sus propias ventas
- ❌ No puede crear/editar productos
- ❌ No puede ver proveedores
- ❌ No puede gestionar inventario

### ADMIN
**Permisos:**
- ✅ Todos los permisos de USER
- ✅ Puede crear/editar productos
- ✅ Puede gestionar proveedores
- ✅ Puede gestionar inventario
- ✅ Puede ver todas las ventas
- ❌ No puede crear/eliminar usuarios
- ❌ No puede gestionar roles

### SUPERADMIN
**Permisos:**
- ✅ Todos los permisos de ADMIN
- ✅ Puede crear/eliminar usuarios
- ✅ **Puede gestionar roles de usuarios**
- ✅ Acceso completo al sistema

## Casos de Uso

### Caso 1: Promover usuario a ADMIN
```bash
# 1. Consultar usuario actual
curl -X GET "http://localhost:8000/role-management/users/{user_id}" \
  -H "Authorization: Bearer YOUR_SUPERADMIN_TOKEN"

# Respuesta: { "roles": ["USER"] }

# 2. Asignar rol ADMIN
curl -X POST "http://localhost:8000/role-management/assign-role" \
  -H "Authorization: Bearer YOUR_SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "{user_id}",
    "role": "ADMIN"
  }'

# Respuesta: { "roles": ["USER", "ADMIN"], "message": "Rol ADMIN asignado exitosamente" }
```

### Caso 2: Remover rol de usuario
```bash
# El usuario tiene ["USER", "ADMIN"]
# Queremos remover ADMIN

curl -X POST "http://localhost:8000/role-management/remove-role" \
  -H "Authorization: Bearer YOUR_SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "{user_id}",
    "role": "ADMIN"
  }'

# Respuesta: { "roles": ["USER"], "message": "Rol ADMIN removido exitosamente" }
```

### Caso 3: Cambiar completamente los roles
```bash
# El usuario tiene ["USER", "ADMIN"]
# Queremos que solo tenga ["SUPERADMIN"]

curl -X PUT "http://localhost:8000/role-management/users/{user_id}/roles" \
  -H "Authorization: Bearer YOUR_SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '["SUPERADMIN"]'

# Respuesta: { "roles": ["SUPERADMIN"], "message": "Roles actualizados exitosamente" }
```

### Caso 4: Ver todos los usuarios y sus roles
```bash
curl -X GET "http://localhost:8000/role-management/users" \
  -H "Authorization: Bearer YOUR_SUPERADMIN_TOKEN"

# Respuesta:
# {
#   "users": [
#     { "email": "user1@example.com", "roles": ["USER"] },
#     { "email": "user2@example.com", "roles": ["USER", "ADMIN"] },
#     { "email": "admin@example.com", "roles": ["SUPERADMIN"] }
#   ],
#   "total": 3
# }
```

## Manejo de Errores

### Error 403: No es SUPERADMIN
```json
{
  "detail": "Solo los usuarios con rol SUPERADMIN pueden gestionar roles. Tus roles actuales: ['USER', 'ADMIN']"
}
```

### Error 400: Usuario ya tiene el rol
```json
{
  "detail": "El usuario ya tiene el rol ADMIN asignado"
}
```

### Error 400: Usuario no tiene el rol
```json
{
  "detail": "El usuario no tiene el rol ADMIN asignado"
}
```

### Error 400: Intentar dejar usuario sin roles
```json
{
  "detail": "No se puede remover el único rol del usuario. Asigne otro rol antes de remover este."
}
```

### Error 400: Intentar remover último SUPERADMIN
```json
{
  "detail": "No se puede remover el rol SUPERADMIN del único SUPERADMIN del sistema. Debe haber al menos un SUPERADMIN."
}
```

### Error 404: Usuario no encontrado
```json
{
  "detail": "Usuario no encontrado"
}
```

### Error 400: Rol inválido
```json
{
  "detail": "Rol inválido: INVALID_ROLE. Roles válidos: ['USER', 'ADMIN', 'SUPERADMIN']"
}
```

## Integración con Frontend

### Ejemplo en JavaScript/React
```javascript
// Servicio para gestión de roles
const roleManagementService = {
  // Obtener todos los usuarios con roles
  async getAllUsers(token) {
    const response = await fetch('http://localhost:8000/role-management/users', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.json();
  },

  // Asignar rol a usuario
  async assignRole(token, userId, role) {
    const response = await fetch('http://localhost:8000/role-management/assign-role', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_id: userId, role })
    });
    return response.json();
  },

  // Remover rol de usuario
  async removeRole(token, userId, role) {
    const response = await fetch('http://localhost:8000/role-management/remove-role', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_id: userId, role })
    });
    return response.json();
  },

  // Obtener roles disponibles
  async getAvailableRoles(token) {
    const response = await fetch('http://localhost:8000/role-management/available-roles', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.json();
  }
};

// Uso en componente React
function UserRoleManagement() {
  const [users, setUsers] = useState([]);
  const token = getAuthToken(); // Función para obtener token

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    const data = await roleManagementService.getAllUsers(token);
    setUsers(data.users);
  };

  const handleAssignRole = async (userId, role) => {
    try {
      await roleManagementService.assignRole(token, userId, role);
      alert('Rol asignado exitosamente');
      loadUsers(); // Recargar lista
    } catch (error) {
      alert('Error asignando rol: ' + error.message);
    }
  };

  return (
    <div>
      <h2>Gestión de Roles</h2>
      {users.map(user => (
        <UserCard 
          key={user.user_id}
          user={user}
          onAssignRole={handleAssignRole}
        />
      ))}
    </div>
  );
}
```

## Testing en Swagger

1. Acceder a `http://localhost:8000/docs`
2. Autenticarse con token de SUPERADMIN
3. Navegar a sección "role-management"
4. Probar endpoints:
   - Ver usuarios: `GET /role-management/users`
   - Asignar rol: `POST /role-management/assign-role`
   - Remover rol: `POST /role-management/remove-role`

## Archivos del Sistema

```
backend/src/
├── schemas/
│   └── role_management.py          # Esquemas Pydantic
├── services/
│   └── role_management_service.py  # Lógica de negocio
└── routers/
    └── role_management.py          # Endpoints
```

## Seguridad y Buenas Prácticas

### ✅ Implementadas
- Autenticación JWT obligatoria
- Verificación de rol SUPERADMIN en todos los endpoints
- Protección del último SUPERADMIN
- Validación de todos los parámetros
- Transacciones de base de datos
- Mensajes de error descriptivos
- Documentación completa en Swagger

### 🔐 Recomendaciones
- Registrar todas las acciones de gestión de roles en logs de auditoría
- Notificar a usuarios cuando sus roles cambien
- Implementar límite de intentos fallidos
- Monitorear actividad de SUPERADMINs

## Próximas Mejoras Sugeridas

1. **Auditoría**: Log de todas las acciones de gestión de roles
2. **Notificaciones**: Enviar email cuando se modifiquen roles
3. **Historial**: Mantener histórico de cambios de roles
4. **Permisos granulares**: Permitir personalizar permisos por usuario
5. **Roles personalizados**: Crear roles custom más allá de USER/ADMIN/SUPERADMIN
6. **Aprobaciones**: Flujo de aprobación para cambios de roles críticos

---

**¡Sistema listo para usar! 🚀**

Consulta `http://localhost:8000/docs` para probar los endpoints interactivamente.
