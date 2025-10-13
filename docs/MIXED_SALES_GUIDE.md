# 🔄 Ventas Mixtas Automáticas - Guía Rápida

## ✅ Respuesta Directa

**SÍ, el sistema soporta ventas mixtas (empaquetado + granel) en una sola transacción de forma AUTOMÁTICA.**

El frontend NO necesita especificar si quiere vender empaquetado o granel. El backend lo decide inteligentemente.

---

## 🎯 Cómo Funciona

### **Frontend Envía (Simple):**
```json
{
  "customer_id": "uuid-cliente",
  "items": [
    {
      "presentation_id": "arroz-1kg-uuid",
      "quantity": 15,
      "unit_price": 4500.0
    }
  ]
}
```

### **Backend Hace (Automático):**

```
Stock Disponible:
├─ Empaquetado: 10 unidades
└─ Granel: 8 kg

Proceso:
1. Vende 10 unidades empaquetadas (agota lotes)
2. Vende 5 kg de granel (quedan 3 kg)
3. Crea 2 SaleDetails:
   ├─ Detail 1: lot_detail_id, quantity: 10
   └─ Detail 2: bulk_conversion_id, quantity: 5

Total vendido: 15 unidades ✅
```

### **Backend Responde:**
```json
{
  "sale_code": "VEN-20251012001",
  "total": 67500.0,
  "items": [
    {
      "presentation_id": "arroz-1kg-uuid",
      "lot_detail_id": "lot-uuid",
      "bulk_conversion_id": null,
      "quantity": 10,
      "line_total": 45000.0
    },
    {
      "presentation_id": "arroz-1kg-uuid",
      "lot_detail_id": null,
      "bulk_conversion_id": "bulk-uuid",
      "quantity": 5,
      "line_total": 22500.0
    }
  ]
}
```

---

## 📊 Estrategia de Venta

```
┌──────────────────────────────────────────┐
│   ALGORITMO DE VENTA AUTOMÁTICA          │
└──────────────────────────────────────────┘

Para cada producto:

1️⃣ VALIDAR STOCK TOTAL
   ├─ Empaquetado: suma de lot_detail.quantity_available
   ├─ Granel: suma de bulk_conversion.remaining_bulk
   └─ Si total < cantidad solicitada → ERROR

2️⃣ INTENTAR VENDER EMPAQUETADO (FIFO)
   ├─ Buscar lotes con stock disponible
   ├─ Ordenar por fecha de recepción
   ├─ Vender hasta agotar cantidad o lotes
   └─ Crear SaleDetail por cada lote usado

3️⃣ SI QUEDA CANTIDAD → VENDER GRANEL
   ├─ Buscar conversiones activas
   ├─ Ordenar por fecha de conversión
   ├─ Vender hasta agotar cantidad
   └─ Crear SaleDetail por cada conversión

4️⃣ ACTUALIZAR INVENTARIO
   ├─ Reducir lot_detail.quantity_available
   ├─ Reducir bulk_conversion.remaining_bulk
   └─ Marcar conversiones como COMPLETED si se agotan
```

---

## 💡 Ejemplos Prácticos

### **Ejemplo 1: Solo Empaquetado**

**Solicitud:**
- Producto: Arroz 1kg
- Cantidad: 5
- Stock empaquetado: 20
- Stock granel: 10

**Resultado:**
- Vende: 5 unidades empaquetadas
- No usa granel (hay suficiente empaquetado)
- 1 SaleDetail con lot_detail_id

---

### **Ejemplo 2: Solo Granel**

**Solicitud:**
- Producto: Arroz 1kg
- Cantidad: 8
- Stock empaquetado: 0
- Stock granel: 15

**Resultado:**
- Vende: 8 kg de granel
- 1 SaleDetail con bulk_conversion_id

---

### **Ejemplo 3: Mixta Automática**

**Solicitud:**
- Producto: Arroz 1kg
- Cantidad: 20
- Stock empaquetado: 12 (Lote A: 7, Lote B: 5)
- Stock granel: 15 (Conversión X: 10, Conversión Y: 5)

**Resultado:**
- Vende: 7 de Lote A → SaleDetail 1 (lot_detail_id = A)
- Vende: 5 de Lote B → SaleDetail 2 (lot_detail_id = B)
- Vende: 8 de Conversión X → SaleDetail 3 (bulk_conversion_id = X)
- **Total: 4 SaleDetails para cumplir 20 unidades**

---

### **Ejemplo 4: Múltiples Productos**

**Solicitud:**
```json
{
  "items": [
    { "presentation_id": "arroz-uuid", "quantity": 10 },
    { "presentation_id": "azucar-uuid", "quantity": 5 },
    { "presentation_id": "frijol-uuid", "quantity": 8 }
  ]
}
```

**Resultado:**
- Arroz: 2 SaleDetails (7 empaquetado + 3 granel)
- Azúcar: 1 SaleDetail (5 empaquetado)
- Frijol: 2 SaleDetails (5 empaquetado + 3 granel)
- **Total: 5 SaleDetails en una sola venta**

---

## 🚨 Manejo de Errores

### **Error: Stock Insuficiente**

```json
{
  "detail": "Stock insuficiente para Arroz Diana 1kg. Disponible: 18 (Empaquetado: 12, Granel: 6), Solicitado: 25"
}
```

**Qué hacer:**
- Ajustar cantidad solicitada
- O esperar nuevo stock

---

## 📝 Checklist Frontend

### **Al Mostrar Productos:**
```javascript
// ✅ Mostrar stock TOTAL
const totalStock = presentation.current_stock + presentation.bulk_stock_available;

// ✅ Permitir venta hasta el máximo total
<input 
  type="number" 
  max={totalStock}
  placeholder={`Máximo: ${totalStock}`}
/>

// ❌ NO separar empaquetado y granel en UI
// El backend lo maneja automáticamente
```

### **Al Crear Venta:**
```javascript
// ✅ Enviar solo presentation_id y quantity
const saleData = {
  customer_id: customerId,
  items: cart.map(item => ({
    presentation_id: item.presentation_id,
    quantity: item.quantity,
    unit_price: item.unit_price
  }))
};

// ❌ NO enviar campos como "is_bulk" o "sale_type"
// No son necesarios
```

### **Al Recibir Respuesta:**
```javascript
// ⚠️ IMPORTANTE: Un producto puede tener múltiples items
const groupByProduct = (saleItems) => {
  const grouped = {};
  
  saleItems.forEach(item => {
    if (!grouped[item.presentation_id]) {
      grouped[item.presentation_id] = {
        total_quantity: 0,
        from_packaged: 0,
        from_bulk: 0
      };
    }
    
    grouped[item.presentation_id].total_quantity += item.quantity;
    
    if (item.lot_detail_id) {
      grouped[item.presentation_id].from_packaged += item.quantity;
    }
    if (item.bulk_conversion_id) {
      grouped[item.presentation_id].from_bulk += item.quantity;
    }
  });
  
  return grouped;
};

// Uso
const grouped = groupByProduct(saleResponse.items);
console.log(grouped);
// {
//   "arroz-uuid": {
//     total_quantity: 15,
//     from_packaged: 10,
//     from_bulk: 5
//   }
// }
```

---

## 🎨 Ejemplo UI Completo

```jsx
const SaleConfirmation = ({ saleResponse }) => {
  // Agrupar items por producto
  const groupedItems = useMemo(() => {
    const groups = {};
    
    saleResponse.items.forEach(item => {
      if (!groups[item.presentation_id]) {
        groups[item.presentation_id] = {
          presentation_id: item.presentation_id,
          total_quantity: 0,
          total_amount: 0,
          unit_price: item.unit_price,
          sources: []
        };
      }
      
      groups[item.presentation_id].total_quantity += item.quantity;
      groups[item.presentation_id].total_amount += item.line_total;
      
      // Agregar detalle de origen
      const source = item.lot_detail_id 
        ? `${item.quantity} empaquetadas`
        : `${item.quantity}kg a granel`;
      groups[item.presentation_id].sources.push(source);
    });
    
    return Object.values(groups);
  }, [saleResponse.items]);
  
  return (
    <div className="sale-confirmation">
      <h2>✅ Venta Confirmada</h2>
      <p>Código: <strong>{saleResponse.sale_code}</strong></p>
      
      <table>
        <thead>
          <tr>
            <th>Producto</th>
            <th>Cantidad</th>
            <th>Origen</th>
            <th>Subtotal</th>
          </tr>
        </thead>
        <tbody>
          {groupedItems.map(item => (
            <tr key={item.presentation_id}>
              <td>{item.presentation_id}</td>
              <td>{item.total_quantity}</td>
              <td>
                {item.sources.map((src, i) => (
                  <div key={i}>{src}</div>
                ))}
              </td>
              <td>${item.total_amount.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
      
      <div className="total">
        <strong>Total: ${saleResponse.total.toLocaleString()}</strong>
      </div>
    </div>
  );
};
```

---

## ✅ Ventajas del Sistema

| Ventaja | Descripción |
|---------|-------------|
| 🤖 **Automático** | Frontend solo envía cantidad, backend decide origen |
| 📦 **FIFO** | Rota inventario automáticamente (más antiguo primero) |
| 🔒 **Atómico** | Toda la venta en una transacción (rollback si falla) |
| 📊 **Optimizado** | Maximiza uso de stock disponible |
| 🛡️ **Validado** | Verifica stock total antes de procesar |
| 🔄 **Cancelable** | Restaura empaquetado y granel correctamente |

---

## 🔍 Preguntas Frecuentes

### **¿Necesito crear dos ventas separadas para empaquetado y granel?**
❌ NO. El sistema lo maneja en una sola venta automáticamente.

### **¿Debo especificar si quiero vender empaquetado o granel?**
❌ NO. El backend decide automáticamente según disponibilidad.

### **¿Puedo forzar que SOLO use empaquetado o SOLO granel?**
❌ NO en la versión actual. El sistema siempre usa estrategia mixta.

### **¿Cómo sé si usó empaquetado o granel?**
✅ Verifica en la respuesta:
- `lot_detail_id != null` → Empaquetado
- `bulk_conversion_id != null` → Granel

### **¿Por qué un producto tiene múltiples items en la respuesta?**
✅ Porque usó diferentes lotes/conversiones. Es normal y esperado.

### **¿Cómo cancelo una venta mixta?**
✅ Usa el mismo endpoint de cancelación. Restaura ambos tipos automáticamente.

---

## 🚀 Conclusión

El sistema de ventas mixtas **simplifica el trabajo del frontend**:
- No necesitas lógica compleja de selección
- No necesitas validaciones separadas
- No necesitas UI diferenciada para empaquetado vs granel

**Solo envía la cantidad que el cliente quiere, y el backend hace el resto.**

---

**Última actualización:** Octubre 12, 2025  
**Versión:** 2.0 (con ventas mixtas automáticas)
