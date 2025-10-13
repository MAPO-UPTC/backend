# 📦➡️🌾 Conversión a Granel - Resumen Rápido

## 🎯 ¿Qué hace este endpoint?

Permite **abrir un bulto/paquete empaquetado** y convertirlo en **stock a granel** para venta en cantidades menores.

---

## 🔗 Endpoint

```
POST /products/open-bulk/
```

**Requiere:** 
- ✅ Bearer Token
- ✅ Permisos `PRODUCTS:UPDATE`

---

## 📥 Request

```json
{
  "source_lot_detail_id": "uuid-del-lote-empaquetado",
  "target_presentation_id": "uuid-de-presentacion-granel",
  "quantity": 500
}
```

**Campos:**
- `source_lot_detail_id`: ID del lote que se va a abrir
- `target_presentation_id`: ID de la presentación "granel" 
- `quantity`: Cantidad de unidades en el paquete (entero)

---

## 📤 Respuesta

```json
{
  "message": "Bulto abierto exitosamente",
  "bulk_conversion_id": "uuid-conversion",
  "converted_quantity": 500,
  "remaining_bulk": 500,
  "status": "ACTIVE"
}
```

---

## 💡 Ejemplo Práctico

### Antes:
- **10 paquetes** de arroz de 500g (empaquetados)
- No se puede vender en cantidades menores

### Después de abrir 1 bulto:
- **9 paquetes** cerrados (empaquetados)
- **500g** disponibles a granel (sueltos)
- Ahora se puede vender 100g, 250g, etc.

---

## 🚀 Implementación Frontend

### 1. Servicio API

```typescript
import axios from 'axios';

export const openBulkConversion = async (
  data: {
    source_lot_detail_id: string;
    target_presentation_id: string;
    quantity: number;
  },
  token: string
) => {
  const response = await axios.post(
    'http://localhost:8000/products/open-bulk/',
    data,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  return response.data;
};
```

### 2. Uso en Componente

```typescript
const handleOpenBulk = async () => {
  try {
    const result = await openBulkConversion({
      source_lot_detail_id: lotId,
      target_presentation_id: granelPresentationId,
      quantity: 500
    }, token);
    
    alert(`✅ ${result.message}\nDisponible: ${result.remaining_bulk}`);
  } catch (error) {
    alert('❌ Error: ' + error.message);
  }
};
```

---

## 🔍 Consultar Stock a Granel

```
GET /products/bulk-stock/
```

**Respuesta:**
```json
[
  {
    "bulk_conversion_id": "uuid",
    "remaining_bulk": 350,
    "converted_quantity": 500,
    "target_presentation_id": "uuid",
    "conversion_date": "2025-10-13T10:30:00",
    "status": "ACTIVE"
  }
]
```

**Interpretación:**
- Se abrió un bulto con 500 unidades
- Se vendieron 150 (500 - 350)
- Quedan 350 disponibles

---

## ⚠️ Validaciones

### Antes de Abrir:
✅ Verificar que `quantity_available >= 1`  
✅ Usuario tiene permiso `PRODUCTS:UPDATE`  
✅ Existe presentación tipo "granel"  
✅ `quantity` es número entero positivo  

---

## 📚 Documentación Completa

Ver **`docs/BULK_CONVERSION_GUIDE.md`** para:
- ✅ Código completo TypeScript/React
- ✅ Hook personalizado `useBulkConversion`
- ✅ Componente modal completo
- ✅ CSS incluido
- ✅ Casos de uso detallados
- ✅ Manejo de errores
- ✅ Checklist de implementación

---

## 🎯 Flujo Completo

1. Usuario ve inventario empaquetado
2. Click en "Abrir para Granel"
3. Selecciona presentación granel y cantidad
4. Backend resta 1 del stock empaquetado
5. Backend crea registro en `bulk_conversion`
6. Ahora se puede vender a granel

---

## ❌ Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| 400 | No hay bultos | Verificar `quantity_available >= 1` |
| 403 | Sin permisos | Usuario necesita `PRODUCTS:UPDATE` |
| 404 | Lote no encontrado | Verificar `source_lot_detail_id` |

---

## ✅ Ventajas

✅ **Flexibilidad**: Vender empaquetado o a granel  
✅ **FIFO**: Sistema usa primero el granel existente  
✅ **Trazabilidad**: Cada conversión queda registrada  
✅ **Control**: Saber qué paquetes están abiertos  

---

**¡Listo para implementar! 🎉**

**Ver guía completa:** `docs/BULK_CONVERSION_GUIDE.md`
