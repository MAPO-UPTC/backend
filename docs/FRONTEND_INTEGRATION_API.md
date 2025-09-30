# MAPO – Documentación de Integración Frontend

## Endpoints y Flujos para Catálogo, Presentaciones y Venta a Granel

---

## 1. Crear Producto con Presentaciones

**POST** `/api/products/`

### Payload ejemplo
```json
{
  "name": "Comida Coquito",
  "description": "Alimento para perros",
  "category_id": "uuid-de-categoria",
  "image_url": "https://ejemplo.com/img.jpg",
  "presentations": [
    {
      "presentation_name": "Bolsa 9kg",
      "quantity": 9,
      "unit": "kg",
      "price": 12000,
      "sku": "COQ-9KG"
    },
    {
      "presentation_name": "Bulto 25kg",
      "quantity": 25,
      "unit": "kg",
      "price": 30000,
      "sku": "COQ-25KG"
    },
    {
      "presentation_name": "Granel",
      "quantity": 1,
      "unit": "kg",
      "price": 1500,
      "sku": "COQ-GRANEL"
    }
  ]
}
```

### Respuesta
```json
{
  "message": "Product created successfully",
  "product": {
    "id": "uuid",
    "name": "Comida Coquito",
    "description": "Alimento para perros",
    "category_id": "uuid-de-categoria",
    "image_url": "https://ejemplo.com/img.jpg"
  }
}
```

---

## 2. Consultar Stock a Granel

**GET** `/api/products/bulk-stock/`

### Respuesta
```json
[
  {
    "bulk_conversion_id": 1,
    "remaining_bulk": 20.0,
    "converted_quantity": 25.0,
    "target_presentation_id": 3,
    "conversion_date": "2025-09-30T12:00:00",
    "status": "ACTIVE"
  }
]
```

---

## 3. Abrir Bulto y Habilitar Venta a Granel

**POST** `/api/products/open-bulk/`

### Payload ejemplo
```json
{
  "source_lot_detail_id": 10,
  "target_presentation_id": 3,
  "quantity": 25.0
}
```

### Respuesta
```json
{
  "bulk_conversion_id": 1,
  "remaining_bulk": 25.0
}
```

---

## 4. Registrar Venta a Granel

**POST** `/api/products/sell-bulk/`

### Payload ejemplo
```json
{
  "bulk_conversion_id": 1,
  "quantity": 2.0,
  "unit_price": 1500,
  "customer_id": 5,
  "user_id": 1
}
```

### Respuesta
```json
{
  "sale_id": "uuid",
  "bulk_conversion_id": 1,
  "remaining_bulk": 23.0
}
```

---

## 5. Ejemplo de integración JS (fetch)

```js
// Crear producto
async function createProduct(product) {
  const res = await fetch('/api/products/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(product)
  });
  return await res.json();
}

// Consultar stock a granel
async function getBulkStock() {
  const res = await fetch('/api/products/bulk-stock/');
  return await res.json();
}

// Abrir bulto
async function openBulk(data) {
  const res = await fetch('/api/products/open-bulk/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return await res.json();
}

// Registrar venta a granel
async function sellBulk(data) {
  const res = await fetch('/api/products/sell-bulk/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return await res.json();
}
```

---

## 6. Consideraciones de UI

- Permitir seleccionar presentación al vender (bolsa, bulto, granel).
- Mostrar el stock a granel disponible antes de permitir la venta.
- Al abrir un bulto, actualizar el stock a granel en la UI.
- Validar que la cantidad a vender no supere el stock disponible a granel.

---

**Fin de la documentación.**
