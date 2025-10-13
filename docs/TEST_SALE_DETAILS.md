# 🧪 Prueba Rápida - Endpoint de Detalles de Venta

## 📝 Instrucciones

### 1. **Obtener el Token de Autenticación**
Primero, haz login para obtener el token:

```bash
# Endpoint de login
POST http://localhost:8000/login

# Body (JSON)
{
  "email": "tu-email@example.com",
  "password": "tu-password"
}

# Respuesta
{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Copia el token** de la respuesta.

---

### 2. **Obtener el ID de una Venta**
Primero necesitas el ID de una venta existente. Puedes obtenerlo del historial:

```bash
GET http://localhost:8000/sales/?limit=10
Authorization: Bearer TU_TOKEN_AQUI
```

**Copia el `id`** de alguna venta de la respuesta.

---

### 3. **Probar el Endpoint de Detalles**

#### Opción A: Usando Swagger (Recomendado)

1. Ve a: http://localhost:8000/docs
2. Haz clic en el candado 🔒 arriba a la derecha
3. Ingresa el token: `Bearer TU_TOKEN`
4. Busca el endpoint: **GET /sales/{sale_id}/details**
5. Haz clic en "Try it out"
6. Pega el `sale_id` de una venta
7. Haz clic en "Execute"
8. Verás la respuesta completa con todos los detalles

---

#### Opción B: Usando PowerShell

```powershell
# Reemplaza estas variables
$token = "TU_TOKEN_AQUI"
$saleId = "550e8400-e29b-41d4-a716-446655440000"

# Hacer la petición
$headers = @{
    "Authorization" = "Bearer $token"
}

$response = Invoke-RestMethod `
    -Uri "http://localhost:8000/sales/$saleId/details" `
    -Method Get `
    -Headers $headers `
    -ContentType "application/json"

# Ver resultado
$response | ConvertTo-Json -Depth 10
```

---

#### Opción C: Usando cURL

```bash
# Reemplaza TU_TOKEN y SALE_ID
curl -X GET "http://localhost:8000/sales/SALE_ID/details" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json"
```

---

#### Opción D: Usando JavaScript (Fetch)

```javascript
const token = 'TU_TOKEN_AQUI';
const saleId = '550e8400-e29b-41d4-a716-446655440000';

fetch(`http://localhost:8000/sales/${saleId}/details`, {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  console.log('Detalles de la venta:', data);
  console.log('Cliente:', data.customer_name);
  console.log('Total:', data.total);
  console.log('Items:', data.items.length);
  
  data.items.forEach((item, index) => {
    console.log(`Item ${index + 1}:`, {
      producto: item.product_name,
      presentacion: item.presentation_name,
      cantidad: item.quantity,
      precioVenta: item.unit_price,
      precioCosto: item.cost_price,
      ganancia: (item.unit_price - item.cost_price) * item.quantity
    });
  });
})
.catch(error => console.error('Error:', error));
```

---

## 📊 Respuesta Esperada

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "sale_code": "VEN-20251012120530",
  "sale_date": "2025-10-12T12:05:30",
  "customer_id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "770e8400-e29b-41d4-a716-446655440002",
  "total": 87.50,
  "status": "completed",
  
  "customer_name": "Juan Carlos Pérez",
  "customer_document": "CC: 1234567890",
  "seller_name": "María García López",
  
  "items": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "sale_id": "550e8400-e29b-41d4-a716-446655440000",
      "presentation_id": "990e8400-e29b-41d4-a716-446655440004",
      "lot_detail_id": "aa0e8400-e29b-41d4-a716-446655440005",
      "bulk_conversion_id": null,
      "quantity": 3,
      "unit_price": 15.50,
      "line_total": 46.50,
      "product_name": "Arroz Diana",
      "presentation_name": "Paquete x 500g",
      "cost_price": 10.20
    },
    {
      "id": "bb0e8400-e29b-41d4-a716-446655440006",
      "sale_id": "550e8400-e29b-41d4-a716-446655440000",
      "presentation_id": "cc0e8400-e29b-41d4-a716-446655440007",
      "lot_detail_id": null,
      "bulk_conversion_id": "dd0e8400-e29b-41d4-a716-446655440008",
      "quantity": 2,
      "unit_price": 20.50,
      "line_total": 41.00,
      "product_name": "Azúcar Manuelita",
      "presentation_name": "Bolsa x 1kg",
      "cost_price": 14.80
    }
  ]
}
```

---

## ✅ Verificaciones

### 1. **Información de la Venta**
- ✅ `sale_code` está presente
- ✅ `sale_date` tiene formato ISO 8601
- ✅ `total` es un número positivo
- ✅ `status` es "completed" o similar

### 2. **Información del Cliente**
- ✅ `customer_name` muestra nombre completo
- ✅ `customer_document` tiene formato "TIPO: NUMERO"

### 3. **Información del Vendedor**
- ✅ `seller_name` muestra nombre completo

### 4. **Items (productos)**
- ✅ `items` es un array con al menos 1 elemento
- ✅ Cada item tiene `product_name` (no es null)
- ✅ Cada item tiene `presentation_name`
- ✅ Cada item tiene `cost_price` (puede ser 0 en algunos casos)
- ✅ `line_total` = `quantity` × `unit_price`

### 5. **Tipos de Venta**
- ✅ Si `lot_detail_id` != null → Venta empaquetada
- ✅ Si `bulk_conversion_id` != null → Venta a granel

---

## 🔍 Cálculos de Ejemplo

Con los datos de respuesta:

```javascript
// Costo total de la venta
const totalCost = items.reduce((sum, item) => 
  sum + (item.cost_price * item.quantity), 0
);
// = (10.20 * 3) + (14.80 * 2) = 30.60 + 29.60 = 60.20

// Ganancia total
const profit = total - totalCost;
// = 87.50 - 60.20 = 27.30

// Margen de ganancia (%)
const margin = (profit / total) * 100;
// = (27.30 / 87.50) * 100 = 31.2%
```

---

## ❌ Errores Comunes

### Error 401: Unauthorized
**Causa**: Token inválido o expirado
**Solución**: Obtén un nuevo token haciendo login

### Error 404: Not Found
**Causa**: El `sale_id` no existe
**Solución**: Verifica que el ID sea correcto usando `GET /sales/`

### Error 500: Internal Server Error
**Causa**: Error en el backend
**Solución**: 
1. Revisa que el servidor esté corriendo
2. Verifica los logs del servidor
3. Asegúrate de que la base de datos esté conectada

---

## 🎯 Siguiente Paso

Una vez que el endpoint funcione correctamente:

1. ✅ Implementa el servicio en tu frontend (ver `SALE_DETAILS_ENDPOINT_GUIDE.md`)
2. ✅ Crea el componente modal para mostrar los detalles
3. ✅ Agrega el botón "Ver Detalles" en tu historial de ventas
4. ✅ Implementa el cálculo de rentabilidad
5. ✅ Agrega funcionalidad de impresión

---

**¡Endpoint listo para usar! 🚀**
