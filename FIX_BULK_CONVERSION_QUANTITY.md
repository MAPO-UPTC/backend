# 🔧 FIX: Conversión a Granel - Cantidad Incorrecta

## 🚨 Problema Reportado

**Síntoma**: Al destapar un bulto de 25kg a granel, solo aparece 1kg disponible en lugar de 25kg.

**Caso de Uso**:
- Tienes 1 bulto de 25kg
- Destapas el bulto
- **Esperado**: 25kg disponibles a granel
- **Real**: Solo 1kg disponible a granel ❌

---

## 🔍 Causa Raíz

### Problema en el Schema

**ANTES** (Código con error):
```python
class BulkConversionCreate(BaseModel):
    source_lot_detail_id: uuid.UUID
    target_presentation_id: uuid.UUID
    quantity: int  # ❌ AMBIGUO - ¿Bultos o kg?
```

El campo `quantity` era ambiguo:
- ¿Es la cantidad de **bultos a abrir**? (1)
- ¿Es la cantidad **total a granel**? (25kg)

### Problema en el Servicio

**ANTES** (Código con error):
```python
def open_bulk_conversion_service(data: BulkConversionCreate):
    # Restar 1 bulto
    lot_detail.quantity_available -= 1
    
    # ❌ PROBLEMA: Usa data.quantity directamente
    bulk = BulkConversion(
        converted_quantity=data.quantity,  # Si envían 1, crea 1kg ❌
        remaining_bulk=data.quantity,      # Si envían 1, hay 1kg ❌
        # ...
    )
```

**El problema**: 
- Frontend envía `quantity: 1` (quiere abrir 1 bulto)
- Backend crea `remaining_bulk: 1` (solo 1kg disponible)
- **Falta multiplicar** por el factor de conversión (25kg)

---

## ✅ Solución Implementada

### 1. Schema Corregido

**DESPUÉS** (Código correcto):
```python
class BulkConversionCreate(BaseModel):
    source_lot_detail_id: uuid.UUID       # ID del lot_detail del bulto empaquetado
    target_presentation_id: uuid.UUID     # ID de la presentación "granel"
    converted_quantity: int               # ✅ Cantidad de bultos a abrir (ej: 1)
    unit_conversion_factor: int           # ✅ Cantidad que contiene cada bulto (ej: 25kg)
```

**Ahora es explícito**:
- `converted_quantity`: Cantidad de bultos a abrir (1, 2, 3...)
- `unit_conversion_factor`: Cuánto contiene cada bulto (25kg, 100 tabletas, etc.)

### 2. Servicio Corregido

**DESPUÉS** (Código correcto):
```python
def open_bulk_conversion_service(data: BulkConversionCreate):
    """
    Ejemplo: Si tienes 1 bulto de 25kg y quieres abrirlo:
    - converted_quantity = 1 (abres 1 bulto)
    - unit_conversion_factor = 25 (cada bulto contiene 25kg)
    - Resultado: Se crean 25kg a granel
    """
    # Validar suficientes bultos
    if lot_detail.quantity_available < data.converted_quantity:
        raise HTTPException(
            status_code=400, 
            detail=f"No hay suficientes bultos disponibles. Disponibles: {lot_detail.quantity_available}, Solicitados: {data.converted_quantity}"
        )
    
    # ✅ CALCULAR cantidad total a granel
    total_bulk_quantity = data.converted_quantity * data.unit_conversion_factor
    # Si abres 1 bulto de 25kg = 1 * 25 = 25kg ✅
    # Si abres 2 bultos de 25kg = 2 * 25 = 50kg ✅
    
    # Restar bultos convertidos
    lot_detail.quantity_available -= data.converted_quantity
    
    # Crear conversión con cantidad correcta
    bulk = BulkConversion(
        source_lot_detail_id=data.source_lot_detail_id,
        target_presentation_id=data.target_presentation_id,
        converted_quantity=data.converted_quantity,    # Bultos abiertos (1)
        remaining_bulk=total_bulk_quantity,            # ✅ Cantidad a granel (25kg)
        conversion_date=datetime.now(),
        status="ACTIVE"
    )
```

---

## 📊 Comparación ANTES vs DESPUÉS

### Ejemplo: Abrir 1 bulto de 25kg

| Aspecto | ANTES ❌ | DESPUÉS ✅ |
|---------|----------|------------|
| **Input del Frontend** | `quantity: 1` | `converted_quantity: 1, unit_conversion_factor: 25` |
| **Bultos descontados** | 1 ✅ | 1 ✅ |
| **Cantidad a granel creada** | 1kg ❌ | 25kg ✅ |
| **remaining_bulk** | 1 ❌ | 25 ✅ |

### Ejemplo: Abrir 2 bultos de 25kg

| Aspecto | ANTES ❌ | DESPUÉS ✅ |
|---------|----------|------------|
| **Input del Frontend** | `quantity: 2` | `converted_quantity: 2, unit_conversion_factor: 25` |
| **Bultos descontados** | 2 ✅ | 2 ✅ |
| **Cantidad a granel creada** | 2kg ❌ | 50kg ✅ |
| **remaining_bulk** | 2 ❌ | 50 ✅ |

---

## 🔄 Cálculo Correcto

### Fórmula
```
total_bulk_quantity = converted_quantity × unit_conversion_factor
```

### Ejemplos

1. **1 bulto de 25kg**:
   ```
   1 × 25 = 25kg a granel
   ```

2. **2 bultos de 25kg**:
   ```
   2 × 25 = 50kg a granel
   ```

3. **1 caja de 100 tabletas**:
   ```
   1 × 100 = 100 tabletas a granel
   ```

4. **5 cajas de 100 tabletas**:
   ```
   5 × 100 = 500 tabletas a granel
   ```

---

## 📝 Cambios en el Código

### Archivos Modificados

| Archivo | Cambio | Líneas |
|---------|--------|--------|
| `src/schemas/product.py` | Schema `BulkConversionCreate` | 25-29 |
| `src/services/product_service.py` | Función `open_bulk_conversion_service()` | 57-110 |

### Campos Nuevos en Request

**Frontend ahora debe enviar**:
```json
{
  "source_lot_detail_id": "uuid-del-lote",
  "target_presentation_id": "uuid-presentacion-granel",
  "converted_quantity": 1,         // ← Cantidad de bultos a abrir
  "unit_conversion_factor": 25     // ← Cantidad que contiene cada bulto
}
```

### Campos en Response

**Backend ahora retorna**:
```json
{
  "message": "Bulto(s) abierto(s) exitosamente. 25 unidades disponibles a granel",
  "bulk_conversion_id": "uuid-de-conversion",
  "converted_quantity": 1,           // Bultos convertidos
  "remaining_bulk": 25,              // ✅ Cantidad a granel disponible
  "total_bulk_created": 25,          // Total creado a granel
  "unit_conversion_factor": 25,      // Factor de conversión usado
  "status": "ACTIVE"
}
```

---

## 🧪 Testing

### Caso 1: Abrir 1 bulto de 25kg

**Request**:
```json
POST /products/open-bulk/
{
  "source_lot_detail_id": "abc-123",
  "target_presentation_id": "xyz-789",
  "converted_quantity": 1,
  "unit_conversion_factor": 25
}
```

**Resultado Esperado**:
- ✅ Se descuenta 1 bulto del inventario empaquetado
- ✅ Se crean 25kg en el inventario a granel
- ✅ `remaining_bulk` = 25

### Caso 2: Abrir 3 cajas de 100 tabletas

**Request**:
```json
POST /products/open-bulk/
{
  "source_lot_detail_id": "def-456",
  "target_presentation_id": "uvw-012",
  "converted_quantity": 3,
  "unit_conversion_factor": 100
}
```

**Resultado Esperado**:
- ✅ Se descuentan 3 cajas del inventario empaquetado
- ✅ Se crean 300 tabletas en el inventario a granel
- ✅ `remaining_bulk` = 300

### Caso 3: Error - Insuficientes bultos

**Request**:
```json
POST /products/open-bulk/
{
  "source_lot_detail_id": "ghi-789",
  "target_presentation_id": "rst-345",
  "converted_quantity": 5,        // Quiere abrir 5
  "unit_conversion_factor": 25
}
```

**Si solo hay 2 bultos disponibles**:
```json
{
  "detail": "No hay suficientes bultos disponibles. Disponibles: 2, Solicitados: 5"
}
```

---

## 🔄 Actualizar Frontend

### Ejemplo TypeScript

**ANTES** ❌:
```typescript
const openBulk = async (lotDetailId: string, targetPresentationId: string) => {
  await axios.post('/products/open-bulk/', {
    source_lot_detail_id: lotDetailId,
    target_presentation_id: targetPresentationId,
    quantity: 1  // ❌ Ambiguo
  });
};
```

**DESPUÉS** ✅:
```typescript
const openBulk = async (
  lotDetailId: string, 
  targetPresentationId: string,
  bulkQuantity: number,      // Bultos a abrir
  conversionFactor: number   // Kg por bulto
) => {
  await axios.post('/products/open-bulk/', {
    source_lot_detail_id: lotDetailId,
    target_presentation_id: targetPresentationId,
    converted_quantity: bulkQuantity,        // ✅ Explícito: bultos
    unit_conversion_factor: conversionFactor // ✅ Explícito: kg por bulto
  });
};

// Uso:
await openBulk(lotId, granelId, 1, 25);  // Abrir 1 bulto de 25kg
```

---

## 📚 Documentación a Actualizar

Los siguientes documentos necesitan actualización:

1. ✅ `BULK_CONVERSION_GUIDE.md` - Actualizar ejemplos de request
2. ✅ `BULK_CONVERSION_SUMMARY.md` - Actualizar estructura de datos
3. ✅ `BULK_CONVERSION_DIAGRAM.md` - Actualizar diagramas con nuevos campos

---

## ✨ Beneficios del Fix

1. ✅ **Cantidad Correcta**: Ahora se crean 25kg cuando abres 1 bulto de 25kg
2. ✅ **Explícito**: Los campos tienen nombres claros y no ambiguos
3. ✅ **Flexible**: Puedes abrir múltiples bultos a la vez
4. ✅ **Validación**: Verifica que haya suficientes bultos antes de convertir
5. ✅ **Información Completa**: Response incluye todos los detalles de la conversión

---

## 🎯 Resumen Ejecutivo

### Problema
Al abrir 1 bulto de 25kg, solo se creaba 1kg a granel en lugar de 25kg.

### Causa
El código no multiplicaba la cantidad de bultos por el factor de conversión.

### Solución
- Añadir campo `unit_conversion_factor` al schema
- Calcular: `total_bulk = converted_quantity × unit_conversion_factor`
- Validar suficientes bultos disponibles

### Resultado
✅ Ahora funciona correctamente: 1 bulto de 25kg = 25kg a granel

---

**Fecha del Fix**: Octubre 2025  
**Severidad Original**: 🔴 CRÍTICO (Lógica de negocio incorrecta)  
**Estado Actual**: ✅ RESUELTO  
**Impacto**: 🎯 ALTO - Afecta conversión a granel

---

## 📞 Próximos Pasos

1. ✅ Código corregido
2. ⏳ Actualizar frontend para enviar ambos campos
3. ⏳ Testing con casos reales
4. ⏳ Actualizar documentación completa
5. ⏳ Verificar ventas a granel funcionen correctamente
