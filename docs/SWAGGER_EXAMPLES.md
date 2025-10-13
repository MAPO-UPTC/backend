# 📋 Ejemplos JSON para Swagger - Sistema de Ventas

## ⚠️ IMPORTANTE
**Campo correcto**: `customer_id` (NO `client_id`)

---

## 🎯 Ejemplos Listos para Usar

### 1️⃣ Venta Simple (1 producto)

```json
{
  "customer_id": "REEMPLAZA-CON-UUID-DEL-CLIENTE",
  "sale_items": [
    {
      "product_id": "REEMPLAZA-CON-UUID-DEL-PRODUCTO",
      "quantity": 10,
      "unit_price": 2500.00
    }
  ],
  "notes": "Venta de prueba desde Swagger"
}
```

---

### 2️⃣ Venta con Múltiples Productos

```json
{
  "customer_id": "REEMPLAZA-CON-UUID-DEL-CLIENTE",
  "sale_items": [
    {
      "product_id": "UUID-PRODUCTO-1",
      "quantity": 10,
      "unit_price": 2500.00
    },
    {
      "product_id": "UUID-PRODUCTO-2",
      "quantity": 5,
      "unit_price": 3500.00
    },
    {
      "product_id": "UUID-PRODUCTO-3",
      "quantity": 20,
      "unit_price": 1200.00
    }
  ],
  "notes": "Venta con varios productos"
}
```

---

### 3️⃣ Venta Grande (Usará Stock Mixto Automático)

```json
{
  "customer_id": "REEMPLAZA-CON-UUID-DEL-CLIENTE",
  "sale_items": [
    {
      "product_id": "REEMPLAZA-CON-UUID-DEL-PRODUCTO",
      "quantity": 150,
      "unit_price": 2500.00
    }
  ],
  "notes": "Venta grande - Backend combinará empaquetado + granel automáticamente"
}
```

**Nota**: Si el producto tiene 10 unidades empaquetadas + 200kg a granel, el backend:
- Vende las 10 empaquetadas
- Vende 140kg del granel
- Total: 150 unidades ✅

---

### 4️⃣ Venta sin Notas

```json
{
  "customer_id": "REEMPLAZA-CON-UUID-DEL-CLIENTE",
  "sale_items": [
    {
      "product_id": "REEMPLAZA-CON-UUID-DEL-PRODUCTO",
      "quantity": 25,
      "unit_price": 4200.50
    }
  ]
}
```

**Nota**: El campo `notes` es opcional.

---

## 🔍 Cómo Obtener los UUIDs Reales

### Para `customer_id`:

1. **Ve a Swagger**: `http://localhost:8000/docs`
2. **Busca**: `GET /api/v1/persons/`
3. **Ejecuta** el endpoint
4. **Copia** el `id` de algún cliente

**Respuesta esperada**:
```json
[
  {
    "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",  // ← Copia este UUID
    "name": "Juan",
    "last_name": "Pérez",
    "full_name": "Juan Pérez",
    ...
  }
]
```

---

### Para `product_id`:

1. **Ve a Swagger**: `http://localhost:8000/docs`
2. **Busca**: `GET /api/v1/products/`
3. **Ejecuta** el endpoint
4. **Copia** el `id` de algún producto

**Respuesta esperada**:
```json
[
  {
    "id": "f7e8d9c0-b1a2-4d3e-9f8a-7b6c5d4e3f2a",  // ← Copia este UUID
    "name": "Arroz Diana",
    "current_stock": 50,
    "bulk_stock_available": 250.5,
    ...
  }
]
```

---

## ✅ Ejemplo con UUIDs Reales

Una vez que tengas los UUIDs, reemplázalos:

```json
{
  "customer_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "sale_items": [
    {
      "product_id": "f7e8d9c0-b1a2-4d3e-9f8a-7b6c5d4e3f2a",
      "quantity": 100,
      "unit_price": 2500.00
    }
  ],
  "notes": "Venta de prueba con UUIDs reales"
}
```

---

## 🎯 Pasos para Probar en Swagger

### Método 1: Desde Swagger UI

1. **Abre**: `http://localhost:8000/docs`
2. **Localiza**: `POST /api/v1/sales/`
3. **Click**: "Try it out"
4. **Pega** uno de los JSONs de arriba
5. **Reemplaza** los UUIDs con los reales (obtenidos de los endpoints GET)
6. **Click**: "Execute"
7. **Observa** la respuesta

---

### Método 2: Desde cURL

```bash
curl -X POST "http://localhost:8000/api/v1/sales/" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "sale_items": [
      {
        "product_id": "f7e8d9c0-b1a2-4d3e-9f8a-7b6c5d4e3f2a",
        "quantity": 10,
        "unit_price": 2500.00
      }
    ],
    "notes": "Venta desde cURL"
  }'
```

---

### Método 3: Desde PowerShell

```powershell
$headers = @{
    "Authorization" = "Bearer TU_TOKEN_AQUI"
    "Content-Type" = "application/json"
}

$body = @{
    customer_id = "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
    sale_items = @(
        @{
            product_id = "f7e8d9c0-b1a2-4d3e-9f8a-7b6c5d4e3f2a"
            quantity = 10
            unit_price = 2500.00
        }
    )
    notes = "Venta desde PowerShell"
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sales/" `
    -Method POST `
    -Headers $headers `
    -Body $body
```

---

## 📊 Respuesta Esperada

### Venta Simple (Stock Empaquetado)

```json
{
  "id": "sale-uuid-123",
  "customer_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "sale_date": "2025-10-12T10:30:00",
  "total_amount": 25000.00,
  "status": "completed",
  "notes": "Venta de prueba desde Swagger",
  "sale_details": [
    {
      "id": "detail-uuid-1",
      "product_id": "f7e8d9c0-b1a2-4d3e-9f8a-7b6c5d4e3f2a",
      "product_name": "Arroz Diana 1kg",
      "quantity": 10,
      "unit_price": 2500.00,
      "subtotal": 25000.00,
      "lot_detail_id": "lot-uuid",
      "bulk_conversion_id": null
    }
  ]
}
```

---

### Venta Mixta (Empaquetado + Granel)

```json
{
  "id": "sale-uuid-456",
  "customer_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "sale_date": "2025-10-12T10:35:00",
  "total_amount": 375000.00,
  "status": "completed",
  "notes": "Venta grande",
  "sale_details": [
    {
      "id": "detail-uuid-1",
      "product_id": "f7e8d9c0-b1a2-4d3e-9f8a-7b6c5d4e3f2a",
      "product_name": "Arroz Diana 1kg",
      "quantity": 10,
      "unit_price": 2500.00,
      "subtotal": 25000.00,
      "lot_detail_id": "lot-uuid",
      "bulk_conversion_id": null
    },
    {
      "id": "detail-uuid-2",
      "product_id": "f7e8d9c0-b1a2-4d3e-9f8a-7b6c5d4e3f2a",
      "product_name": "Arroz Diana 1kg",
      "quantity": 140,
      "unit_price": 2500.00,
      "subtotal": 350000.00,
      "lot_detail_id": null,
      "bulk_conversion_id": "bulk-uuid"
    }
  ]
}
```

**⚠️ Observa**: El mismo producto aparece **2 veces** en `sale_details`:
- Una con `lot_detail_id` (empaquetado)
- Otra con `bulk_conversion_id` (granel)

---

## ❌ Errores Comunes

### Error 422: Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "customer_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Causa**: Usaste `client_id` en lugar de `customer_id`  
**Solución**: Cambia a `customer_id`

---

### Error 400: Stock Insuficiente

```json
{
  "detail": "Stock insuficiente para el producto Arroz Diana 1kg. Disponible: 5, Solicitado: 10"
}
```

**Causa**: No hay suficiente stock (empaquetado + granel)  
**Solución**: Reduce la cantidad o verifica el stock con `GET /api/v1/products/`

---

### Error 404: Cliente no encontrado

```json
{
  "detail": "Cliente no encontrado"
}
```

**Causa**: El `customer_id` no existe en la base de datos  
**Solución**: Verifica el UUID con `GET /api/v1/persons/`

---

### Error 404: Producto no encontrado

```json
{
  "detail": "Producto no encontrado"
}
```

**Causa**: El `product_id` no existe en la base de datos  
**Solución**: Verifica el UUID con `GET /api/v1/products/`

---

## 🎯 Checklist Antes de Crear una Venta

- [ ] ✅ Obtuve el `customer_id` de `GET /api/v1/persons/`
- [ ] ✅ Obtuve el `product_id` de `GET /api/v1/products/`
- [ ] ✅ Verifiqué que hay stock suficiente (`current_stock` + `bulk_stock_available`)
- [ ] ✅ Usé `customer_id` (NO `client_id`)
- [ ] ✅ El `unit_price` es un número decimal (ej: 2500.00)
- [ ] ✅ La `quantity` es un número entero (ej: 10)
- [ ] ✅ Incluí el header `Authorization` si es necesario

---

## 📚 Documentación Relacionada

- **[FRONTEND_QUICK_SALE_GUIDE.md](./FRONTEND_QUICK_SALE_GUIDE.md)** - Guía paso a paso completa
- **[SALES_SYSTEM_COMPLETE_GUIDE.md](./SALES_SYSTEM_COMPLETE_GUIDE.md)** - Documentación completa del sistema
- **[MIXED_SALES_GUIDE.md](./MIXED_SALES_GUIDE.md)** - Guía de ventas mixtas

---

## 💡 Tips Adicionales

### Verificar Stock Antes de Vender

```json
// GET /api/v1/products/{product_id}
{
  "id": "f7e8d9c0-b1a2-4d3e-9f8a-7b6c5d4e3f2a",
  "name": "Arroz Diana 1kg",
  "current_stock": 10,           // Stock empaquetado
  "bulk_stock_available": 250.5  // Stock a granel
}

// Stock total disponible: 10 + 250.5 = 260.5 unidades
```

### Obtener Precio Sugerido

```json
// GET /api/v1/products/{product_id}
{
  "presentations": [
    {
      "id": "presentation-uuid",
      "name": "1kg",
      "sale_price": 2500.00  // ← Usa este precio
    }
  ]
}
```

### Ver Historial de Ventas

```json
// GET /api/v1/sales/
// Muestra todas las ventas realizadas
```

### Ver Detalle de una Venta

```json
// GET /api/v1/sales/{sale_id}
// Muestra los detalles completos de una venta específica
```

### Cancelar una Venta

```json
// POST /api/v1/sales/{sale_id}/cancel
// Cancela una venta y restaura el inventario
```

---

## 🚀 Ejemplo Completo de Flujo

```javascript
// 1. Obtener cliente
const customers = await fetch('http://localhost:8000/api/v1/persons/');
const customerList = await customers.json();
const customer_id = customerList[0].id;

// 2. Obtener productos
const products = await fetch('http://localhost:8000/api/v1/products/');
const productList = await products.json();
const product_id = productList[0].id;
const unit_price = productList[0].presentations[0].sale_price;

// 3. Crear venta
const sale = await fetch('http://localhost:8000/api/v1/sales/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token_aqui'
  },
  body: JSON.stringify({
    customer_id: customer_id,  // ✅ customer_id
    sale_items: [
      {
        product_id: product_id,
        quantity: 10,
        unit_price: unit_price
      }
    ],
    notes: "Venta automatizada"
  })
});

const result = await sale.json();
console.log('Venta creada:', result);
```

---

## ✅ Resumen

- **Campo correcto**: `customer_id` (NO `client_id`)
- **Obtener UUIDs**: Desde `GET /api/v1/persons/` y `GET /api/v1/products/`
- **Ventas mixtas**: El backend las maneja automáticamente
- **Validación**: Siempre verifica el stock antes de vender
- **Testing**: Usa Swagger para probar rápidamente

---

🎉 **¡Con estos ejemplos puedes empezar a probar las ventas inmediatamente!**
