# 🚀 Guía Rápida: Cómo Hacer una Venta (Frontend)

## 📌 Información Importante

**Campo correcto**: `customer_id` (NO `client_id`)

---

## ✅ Paso a Paso para Implementar Ventas

### **1️⃣ Obtener el Cliente**

```javascript
// GET /api/v1/persons/
const customers = await fetch('http://localhost:8000/api/v1/persons/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

const customerList = await customers.json();
// Selecciona un customer_id de la lista
const customer_id = customerList[0].id; // UUID del cliente
```

---

### **2️⃣ Obtener Productos Disponibles**

```javascript
// GET /api/v1/products/
const products = await fetch('http://localhost:8000/api/v1/products/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

const productList = await products.json();

// Cada producto tiene:
// - id: UUID del producto
// - name: Nombre del producto
// - current_stock: Stock empaquetado disponible
// - bulk_stock_available: Stock a granel disponible
// - presentations: Array de presentaciones con sus precios
```

---

### **3️⃣ Crear la Venta**

#### **Estructura del JSON**

```json
{
  "customer_id": "UUID-DEL-CLIENTE",
  "sale_items": [
    {
      "product_id": "UUID-DEL-PRODUCTO",
      "quantity": 10,
      "unit_price": 2500.00
    }
  ],
  "notes": "Venta de prueba"
}
```

#### **Código JavaScript/TypeScript**

```javascript
async function createSale(customerId, saleItems, notes = "") {
  const saleData = {
    customer_id: customerId, // ⚠️ IMPORTANTE: customer_id, NO client_id
    sale_items: saleItems.map(item => ({
      product_id: item.productId,
      quantity: item.quantity,
      unit_price: item.unitPrice
    })),
    notes: notes
  };

  const response = await fetch('http://localhost:8000/api/v1/sales/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(saleData)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al crear la venta');
  }

  return await response.json();
}
```

---

## 📝 Ejemplos Completos

### **Ejemplo 1: Venta Simple (1 producto)**

```json
{
  "customer_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "sale_items": [
    {
      "product_id": "f7e8d9c0-b1a2-4d3e-9f8a-7b6c5d4e3f2a",
      "quantity": 10,
      "unit_price": 2500.00
    }
  ],
  "notes": "Venta al por mayor"
}
```

### **Ejemplo 2: Venta con Múltiples Productos**

```json
{
  "customer_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "sale_items": [
    {
      "product_id": "f7e8d9c0-b1a2-4d3e-9f8a-7b6c5d4e3f2a",
      "quantity": 10,
      "unit_price": 2500.00
    },
    {
      "product_id": "1a2b3c4d-5e6f-4g7h-8i9j-0k1l2m3n4o5p",
      "quantity": 5,
      "unit_price": 3500.00
    },
    {
      "product_id": "9z8y7x6w-5v4u-4t3s-2r1q-0p9o8n7m6l5k",
      "quantity": 20,
      "unit_price": 1200.00
    }
  ],
  "notes": "Venta mixta - varios productos"
}
```

### **Ejemplo 3: Venta que Usará Stock Mixto (Empaquetado + Granel)**

```json
{
  "customer_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "sale_items": [
    {
      "product_id": "f7e8d9c0-b1a2-4d3e-9f8a-7b6c5d4e3f2a",
      "quantity": 150,
      "unit_price": 2500.00
    }
  ],
  "notes": "Venta grande - backend combinará empaquetado + granel automáticamente"
}
```

**Nota**: Si el producto tiene 10 unidades empaquetadas y 200kg a granel, el backend automáticamente:
- Vende las 10 empaquetadas
- Vende 140kg del granel
- Total: 150 unidades ✅

---

## 🎯 Respuesta del Backend

### **Venta Simple**

```json
{
  "id": "sale-uuid-123",
  "customer_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "sale_date": "2025-10-12T10:30:00",
  "total_amount": 25000.00,
  "status": "completed",
  "notes": "Venta al por mayor",
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

### **Venta Mixta (Empaquetado + Granel)**

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

**⚠️ IMPORTANTE**: Observa que el **mismo producto aparece 2 veces** en `sale_details`:
- Una con `lot_detail_id` → Stock empaquetado
- Otra con `bulk_conversion_id` → Stock a granel

---

## 🔧 Código React Completo

### **Hook Personalizado para Ventas**

```typescript
// hooks/useSales.ts
import { useState } from 'react';

interface SaleItem {
  productId: string;
  quantity: number;
  unitPrice: number;
}

interface CreateSaleRequest {
  customer_id: string;  // ⚠️ customer_id, NO client_id
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

  const createSale = async (
    customerId: string,
    saleItems: SaleItem[],
    notes?: string
  ) => {
    setLoading(true);
    setError(null);

    try {
      const requestBody: CreateSaleRequest = {
        customer_id: customerId, // ⚠️ IMPORTANTE
        sale_items: saleItems.map(item => ({
          product_id: item.productId,
          quantity: item.quantity,
          unit_price: item.unitPrice
        })),
        notes: notes || ""
      };

      const response = await fetch('http://localhost:8000/api/v1/sales/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al crear la venta');
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

### **Componente de Formulario de Venta**

```tsx
// components/SaleForm.tsx
import React, { useState } from 'react';
import { useSales } from '../hooks/useSales';

interface CartItem {
  productId: string;
  productName: string;
  quantity: number;
  unitPrice: number;
}

export function SaleForm() {
  const [customerId, setCustomerId] = useState('');
  const [cart, setCart] = useState<CartItem[]>([]);
  const [notes, setNotes] = useState('');
  const { createSale, loading, error } = useSales();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!customerId) {
      alert('Debes seleccionar un cliente');
      return;
    }

    if (cart.length === 0) {
      alert('Debes agregar al menos un producto');
      return;
    }

    try {
      const sale = await createSale(
        customerId,
        cart.map(item => ({
          productId: item.productId,
          quantity: item.quantity,
          unitPrice: item.unitPrice
        })),
        notes
      );

      alert(`Venta creada exitosamente! ID: ${sale.id}`);
      // Limpiar formulario
      setCart([]);
      setNotes('');
    } catch (err) {
      console.error('Error al crear venta:', err);
    }
  };

  const totalAmount = cart.reduce(
    (sum, item) => sum + (item.quantity * item.unitPrice),
    0
  );

  return (
    <form onSubmit={handleSubmit}>
      <h2>Nueva Venta</h2>

      {/* Selector de Cliente */}
      <div>
        <label>Cliente:</label>
        <select
          value={customerId}
          onChange={(e) => setCustomerId(e.target.value)}
          required
        >
          <option value="">Seleccionar cliente...</option>
          {/* Aquí cargarías los clientes de /api/v1/persons/ */}
        </select>
      </div>

      {/* Carrito de Compras */}
      <div>
        <h3>Productos</h3>
        {cart.map((item, index) => (
          <div key={index}>
            <span>{item.productName}</span>
            <span>Cantidad: {item.quantity}</span>
            <span>Precio: ${item.unitPrice}</span>
            <span>Subtotal: ${item.quantity * item.unitPrice}</span>
          </div>
        ))}
      </div>

      {/* Total */}
      <div>
        <strong>Total: ${totalAmount.toFixed(2)}</strong>
      </div>

      {/* Notas */}
      <div>
        <label>Notas (opcional):</label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Agregar comentarios sobre la venta..."
        />
      </div>

      {/* Botón de Envío */}
      <button type="submit" disabled={loading}>
        {loading ? 'Procesando...' : 'Crear Venta'}
      </button>

      {/* Errores */}
      {error && (
        <div style={{ color: 'red' }}>
          Error: {error}
        </div>
      )}
    </form>
  );
}
```

---

## ⚠️ Errores Comunes

### **1. Error 422: Validation Error**

**Causa**: Campo incorrecto o faltante

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

**Solución**: Asegúrate de usar `customer_id`, NO `client_id`

---

### **2. Error 400: Stock Insuficiente**

```json
{
  "detail": "Stock insuficiente para el producto Arroz Diana 1kg. Disponible: 5, Solicitado: 10"
}
```

**Solución**: Verifica el stock disponible antes de crear la venta con `GET /api/v1/products/`

---

### **3. Error 404: Cliente no encontrado**

```json
{
  "detail": "Cliente no encontrado"
}
```

**Solución**: Verifica que el `customer_id` exista en la base de datos

---

## 🎯 Checklist de Implementación

- [ ] ✅ Usar `customer_id` (NO `client_id`)
- [ ] ✅ Validar que `customer_id` existe antes de crear la venta
- [ ] ✅ Verificar stock disponible antes de agregar al carrito
- [ ] ✅ Calcular el total correctamente (quantity × unit_price)
- [ ] ✅ Manejar errores de validación (422)
- [ ] ✅ Manejar errores de stock insuficiente (400)
- [ ] ✅ Mostrar confirmación después de crear la venta
- [ ] ✅ Limpiar el formulario después de una venta exitosa
- [ ] ✅ Agrupar `sale_details` del mismo producto para mostrar en UI
- [ ] ✅ Incluir Authorization header en todas las peticiones

---

## 🔗 Endpoints Relacionados

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/persons/` | GET | Obtener lista de clientes |
| `/api/v1/products/` | GET | Obtener productos con stock |
| `/api/v1/sales/` | POST | Crear nueva venta |
| `/api/v1/sales/` | GET | Listar todas las ventas |
| `/api/v1/sales/{sale_id}` | GET | Obtener detalle de una venta |
| `/api/v1/sales/{sale_id}/cancel` | POST | Cancelar una venta |

---

## 📚 Documentación Adicional

- **[SALES_SYSTEM_COMPLETE_GUIDE.md](./SALES_SYSTEM_COMPLETE_GUIDE.md)** - Guía completa del sistema de ventas
- **[MIXED_SALES_GUIDE.md](./MIXED_SALES_GUIDE.md)** - Guía específica de ventas mixtas
- **[API Swagger](http://localhost:8000/docs)** - Documentación interactiva de la API

---

## 💡 Resumen Rápido

```javascript
// 1. Obtener customer_id
const customers = await fetch('/api/v1/persons/');
const customer_id = customers[0].id;

// 2. Crear venta
const sale = await fetch('/api/v1/sales/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    customer_id: customer_id,  // ⚠️ IMPORTANTE
    sale_items: [
      {
        product_id: "uuid-producto",
        quantity: 10,
        unit_price: 2500.00
      }
    ],
    notes: "Venta de prueba"
  })
});

const result = await sale.json();
console.log('Venta creada:', result.id);
```

---

## 🎉 ¡Listo!

Con esta guía el frontend puede implementar el sistema de ventas correctamente. El backend se encarga automáticamente de:

- ✅ Validar stock disponible
- ✅ Combinar stock empaquetado + granel (ventas mixtas)
- ✅ Descontar inventario automáticamente
- ✅ Generar código de venta único
- ✅ Aplicar estrategia FIFO para optimizar inventario

**¿Dudas?** Revisa los ejemplos completos o consulta la documentación detallada.
