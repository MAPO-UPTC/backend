# Recuperación de Contraseña y Cliente Genérico

## 📧 Sistema de Recuperación de Contraseña

### Descripción
Sistema seguro de recuperación de contraseña mediante código de 6 dígitos enviado por email.

### Endpoints

#### 1. Solicitar Cambio de Contraseña
```
POST /users/request-password-reset
```

**Body:**
```json
{
  "email": "usuario@ejemplo.com"
}
```

**Respuesta:**
```json
{
  "message": "Si el email está registrado, recibirás un código de recuperación.",
  "email": "usuario@ejemplo.com"
}
```

**Características:**
- ✅ Endpoint público (no requiere autenticación)
- ✅ No revela si el email existe (seguridad)
- ✅ Código de 6 dígitos
- ✅ Válido por 15 minutos
- ✅ Máximo 3 intentos de validación
- ✅ Email en HTML con diseño profesional

#### 2. Confirmar Cambio de Contraseña
```
POST /users/reset-password
```

**Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "reset_code": "123456",
  "new_password": "nuevaContraseña123"
}
```

**Respuesta:**
```json
{
  "message": "Password updated successfully",
  "email": "usuario@ejemplo.com"
}
```

**Validaciones:**
- ✅ Código válido y no expirado
- ✅ Usuario existe en base de datos
- ✅ Actualiza contraseña en Firebase
- ✅ Limpia código después de uso

### Configuración de Email (Variables de Entorno)

Para que el envío de emails funcione en producción, configurar:

```bash
# SMTP Configuration (Gmail example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
SMTP_FROM_EMAIL=tu-email@gmail.com
SMTP_FROM_NAME=MAPO Sistema
```

**Nota para Gmail:**
- Usar "App Password" en lugar de la contraseña normal
- Generar en: https://myaccount.google.com/apppasswords

**Modo Desarrollo:**
- Si las variables no están configuradas, el sistema simula el envío
- El código se imprime en consola para testing

---

## 👤 Cliente Genérico para Ventas sin Registro

### Problema
No todos los clientes necesitan estar registrados en el sistema para realizar ventas.

### Solución
Cliente genérico con UUID fijo que se usa para ventas a personas no registradas.

### UUID del Cliente Genérico
```
00000000-0000-0000-0000-000000000001
```

### Crear Cliente Genérico en Base de Datos

#### Opción 1: Script Python
```bash
cd backend
python create_generic_client.py
```

#### Opción 2: SQL Directo
```sql
INSERT INTO person (id, name, last_name, document_type, document_number)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Cliente',
    'Genérico',
    'CC',
    '0000000000'
);
```

### Uso en el Frontend

Al realizar una venta, si el cliente no está registrado:

```javascript
const saleData = {
  customer_id: "00000000-0000-0000-0000-000000000001", // Cliente genérico
  user_id: currentUserId,
  items: [
    // ... detalles de la venta
  ]
};

await fetch('/sales/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(saleData)
});
```

### Ventajas

✅ **Simplicidad**: No requiere crear cliente para cada venta casual
✅ **Trazabilidad**: Todas las ventas quedan registradas
✅ **Reportes**: Las ventas genéricas se pueden filtrar en reportes
✅ **Flexibilidad**: Permite ventas rápidas sin burocracia
✅ **Base de datos consistente**: UUID fijo facilita consultas

### Reportes y Filtros

Las ventas al cliente genérico se pueden identificar fácilmente:

```sql
-- Ventas a clientes registrados (excluir genérico)
SELECT * FROM sale 
WHERE customer_id != '00000000-0000-0000-0000-000000000001';

-- Solo ventas genéricas
SELECT * FROM sale 
WHERE customer_id = '00000000-0000-0000-0000-000000000001';

-- Contar ventas por tipo
SELECT 
  CASE 
    WHEN customer_id = '00000000-0000-0000-0000-000000000001' 
    THEN 'Cliente Genérico'
    ELSE 'Cliente Registrado'
  END as tipo_cliente,
  COUNT(*) as total_ventas,
  SUM(total) as total_monto
FROM sale
GROUP BY tipo_cliente;
```

---

## 🧪 Testing

### Test Recuperación de Contraseña

```bash
# 1. Solicitar código
curl -X POST http://localhost:8000/users/request-password-reset \
  -H "Content-Type: application/json" \
  -d '{"email": "usuario@ejemplo.com"}'

# 2. Cambiar contraseña (usar código del email)
curl -X POST http://localhost:8000/users/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "reset_code": "123456",
    "new_password": "NuevaContraseña123"
  }'
```

### Test Cliente Genérico

```bash
# 1. Crear cliente genérico
python create_generic_client.py

# 2. Verificar que existe
curl http://localhost:8000/clients/00000000-0000-0000-0000-000000000001 \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Realizar venta con cliente genérico
curl -X POST http://localhost:8000/sales/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "customer_id": "00000000-0000-0000-0000-000000000001",
    "user_id": "YOUR_USER_ID",
    "items": [...]
  }'
```

---

## 📝 Notas de Implementación

### Seguridad del Sistema de Reset

1. **Códigos temporales**: Expiran en 15 minutos
2. **Límite de intentos**: Máximo 3 intentos por código
3. **No revela información**: Mismo mensaje si email existe o no
4. **Limpieza automática**: Códigos se eliminan después de uso
5. **Almacenamiento temporal**: En memoria (usar Redis en producción)

### Mejoras Futuras

#### Para Recuperación de Contraseña:
- [ ] Usar Redis para almacenar códigos (en lugar de memoria)
- [ ] Rate limiting por IP
- [ ] Logs de intentos de reset
- [ ] Notificación de cambio exitoso por email
- [ ] Opción de reset por SMS

#### Para Cliente Genérico:
- [ ] Opción de convertir venta genérica a cliente registrado
- [ ] Campo de notas para identificar cliente genérico
- [ ] Dashboard con estadísticas de ventas genéricas vs registradas
- [ ] Exportar lista de clientes frecuentes sin registro (para campaña de registro)
