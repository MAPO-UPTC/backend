# 🔧 Corrección: Items en Historial de Ventas

## ❌ Problema Detectado

El endpoint `GET /sales/` no devolvía los `items` (detalles) de cada venta.

**Causa**: El modelo `Sale` en la base de datos no tenía definida la relación con `SaleDetail`.

---

## ✅ Solución Implementada

### **Archivo modificado**: `src/models_db.py`

#### **1. Agregada relación en modelo `Sale`**

```python
class Sale(Base):
    __tablename__ = "sale"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    sale_code: Mapped[str] = mapped_column(String, nullable=False)
    sale_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("person.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("user.id"), nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    
    # ✅ AGREGADO: Relación con SaleDetail
    items: Mapped[list["SaleDetail"]] = relationship("SaleDetail", back_populates="sale", lazy="joined")
```

**Parámetro `lazy="joined"`**: Carga automáticamente los items con cada venta (en una sola query).

---

#### **2. Agregada relación inversa en `SaleDetail`**

```python
class SaleDetail(Base):
    __tablename__ = "sale_detail"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    sale_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("sale.id"), nullable=False)
    presentation_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("product_presentation.id"), nullable=False)
    lot_detail_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("lot_detail.id"), nullable=False)
    bulk_conversion_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("bulk_conversion.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    line_total: Mapped[float] = mapped_column(Float, nullable=False)
    
    # ✅ AGREGADO: Relación inversa con Sale
    sale: Mapped["Sale"] = relationship("Sale", back_populates="items")
```

---

## 📊 Respuesta Ahora Incluye Items

### **Antes (sin items):**

```json
{
  "id": "uuid-venta",
  "sale_code": "VEN-20251012143000",
  "customer_id": "uuid-cliente",
  "user_id": "uuid-usuario",
  "sale_date": "2025-10-12T14:30:00",
  "total": 125000.00,
  "status": "completed",
  "items": []  // ❌ Vacío
}
```

---

### **Ahora (con items):**

```json
{
  "id": "uuid-venta",
  "sale_code": "VEN-20251012143000",
  "customer_id": "uuid-cliente",
  "user_id": "uuid-usuario",
  "sale_date": "2025-10-12T14:30:00",
  "total": 125000.00,
  "status": "completed",
  "items": [  // ✅ Con datos
    {
      "id": "uuid-detalle-1",
      "sale_id": "uuid-venta",
      "presentation_id": "uuid-presentacion",
      "lot_detail_id": "uuid-lote",
      "bulk_conversion_id": null,
      "quantity": 10,
      "unit_price": 2500.00,
      "line_total": 25000.00
    },
    {
      "id": "uuid-detalle-2",
      "sale_id": "uuid-venta",
      "presentation_id": "uuid-presentacion",
      "lot_detail_id": null,
      "bulk_conversion_id": "uuid-bulk",
      "quantity": 40,
      "unit_price": 2500.00,
      "line_total": 100000.00
    }
  ]
}
```

---

## 🎯 Cambios en el Frontend

### **Antes:**

```typescript
// items venía vacío []
const sales = await fetch('/sales/');
console.log(sales[0].items); // []
```

---

### **Ahora:**

```typescript
// items viene con datos
const sales = await fetch('/sales/');
console.log(sales[0].items); 
// [
//   { id: "...", quantity: 10, unit_price: 2500, ... },
//   { id: "...", quantity: 40, unit_price: 2500, ... }
// ]

// Puedes iterar sobre los items
sales.forEach(sale => {
  console.log(`Venta ${sale.sale_code}:`);
  sale.items.forEach(item => {
    console.log(`  - ${item.quantity} unidades a $${item.unit_price}`);
  });
});
```

---

## 🔄 Actualización Necesaria

### **¿Necesitas reiniciar el servidor?**

✅ **Sí**, reinicia el servidor backend para que cargue los modelos actualizados:

```powershell
# Detén el servidor (Ctrl+C)
# Luego reinicia
python -m uvicorn src.main:app --reload --port 8000
```

---

## ✅ Verificación

### **Prueba en Swagger**

1. Ve a: `http://localhost:8000/docs`
2. Busca: `GET /sales/`
3. Ejecuta el endpoint
4. Verifica que cada venta tenga su array de `items` con datos

---

### **Prueba desde el Frontend**

```javascript
const response = await fetch('http://localhost:8000/sales/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  }
});

const sales = await response.json();

console.log('Primera venta:', sales[0]);
console.log('Items de la primera venta:', sales[0].items);
console.log('Cantidad de items:', sales[0].items.length);
```

**Resultado esperado:**
```
Primera venta: { id: "...", sale_code: "VEN-...", total: 125000, ... }
Items de la primera venta: [ { id: "...", quantity: 10, ... }, { id: "...", quantity: 40, ... } ]
Cantidad de items: 2
```

---

## 📝 Estructura del Item

Cada item en el array tiene:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | ID único del detalle |
| `sale_id` | UUID | ID de la venta a la que pertenece |
| `presentation_id` | UUID | ID de la presentación del producto |
| `lot_detail_id` | UUID o null | ID del lote (si es empaquetado) |
| `bulk_conversion_id` | UUID o null | ID de la conversión a granel (si es granel) |
| `quantity` | integer | Cantidad vendida |
| `unit_price` | float | Precio unitario |
| `line_total` | float | Total de la línea (quantity × unit_price) |

---

## 💡 Ventajas de la Relación

### **1. Carga Automática**

Con `lazy="joined"`, los items se cargan automáticamente en una sola query SQL (JOIN).

```sql
-- Una sola query eficiente
SELECT sale.*, sale_detail.*
FROM sale
LEFT JOIN sale_detail ON sale.id = sale_detail.sale_id
ORDER BY sale.sale_date DESC
LIMIT 100;
```

---

### **2. Menos Código**

No necesitas hacer queries adicionales para obtener los detalles:

```python
# ❌ Antes (dos queries)
sale = db.query(Sale).first()
details = db.query(SaleDetail).filter(SaleDetail.sale_id == sale.id).all()

# ✅ Ahora (una query)
sale = db.query(Sale).first()
# sale.items ya está cargado automáticamente
```

---

### **3. Serialización Automática**

Pydantic convierte la relación automáticamente:

```python
# El schema SaleResponse incluye items
class SaleResponse(BaseModel):
    id: uuid.UUID
    sale_code: str
    # ... otros campos ...
    items: List[SaleDetailResponse] = Field(default=[])
    
    class Config:
        from_attributes = True  # ← Clave para que funcione

# SQLAlchemy → Pydantic → JSON (automático)
```

---

## 🎨 Ejemplo de Uso en el Frontend

### **Componente React para Mostrar Items**

```tsx
interface SaleItem {
  id: string;
  presentation_id: string;
  quantity: number;
  unit_price: number;
  line_total: number;
  lot_detail_id: string | null;
  bulk_conversion_id: string | null;
}

interface Sale {
  id: string;
  sale_code: string;
  sale_date: string;
  total: number;
  items: SaleItem[];
}

function SaleDetailsView({ sale }: { sale: Sale }) {
  return (
    <div className="sale-details">
      <h3>Venta {sale.sale_code}</h3>
      <p>Fecha: {new Date(sale.sale_date).toLocaleString()}</p>
      
      <table>
        <thead>
          <tr>
            <th>Presentación</th>
            <th>Cantidad</th>
            <th>Precio Unit.</th>
            <th>Subtotal</th>
            <th>Origen</th>
          </tr>
        </thead>
        <tbody>
          {sale.items.map((item) => (
            <tr key={item.id}>
              <td>{item.presentation_id}</td>
              <td>{item.quantity}</td>
              <td>${item.unit_price.toFixed(2)}</td>
              <td>${item.line_total.toFixed(2)}</td>
              <td>
                {item.lot_detail_id ? (
                  <span className="badge empaquetado">Empaquetado</span>
                ) : (
                  <span className="badge granel">Granel</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      <div className="total">
        <strong>Total: ${sale.total.toFixed(2)}</strong>
      </div>
    </div>
  );
}
```

---

## 📋 Checklist Post-Corrección

- [ ] ✅ Reiniciar el servidor backend
- [ ] ✅ Probar en Swagger que `items` viene con datos
- [ ] ✅ Verificar desde el frontend que `sales[0].items.length > 0`
- [ ] ✅ Actualizar componentes frontend para mostrar los items
- [ ] ✅ Verificar que ventas mixtas muestran múltiples items

---

## 🚀 Resultado Final

Ahora el endpoint `GET /sales/` devuelve:
- ✅ Lista de ventas ordenadas (más recientes primero)
- ✅ Cada venta con su array de `items` completo
- ✅ Filtros opcionales por fecha funcionando
- ✅ Paginación funcionando
- ✅ Una sola query SQL eficiente (JOIN)

---

¿Necesitas más ayuda con la implementación en el frontend? 🎯
