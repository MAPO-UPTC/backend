# Tarjeta de Referencia Rápida: Endpoint Lot Details

## 🔌 Endpoint

```
GET /inventory/presentations/{presentation_id}/lot-details?available_only=true
```

## 📥 Ejemplo de Uso

```typescript
// 1. Llamar al endpoint
const response = await inventoryService.getLotDetailsByPresentation(presentationId);

// 2. Obtener lote más antiguo (FIFO)
const oldestLot = response.data[0];  // ← Primera posición = más antiguo

// 3. Usar en conversión
await productService.openBulkConversion({
  lot_detail_id: oldestLot.id,
  converted_quantity: 1,
  unit_conversion_factor: 100
});
```

## 📊 Estructura de Respuesta

```json
{
  "success": true,
  "data": [
    {
      "id": "lot_detail_id",              // ← Usar para conversiones
      "lot_code": "LOT-2024-001",
      "batch_number": "BATCH-2024-001",
      "received_date": "2024-01-15T10:30:00",
      "expiry_date": "2025-01-15T23:59:59",
      "quantity_available": 75,
      "quantity_received": 100,
      "unit_cost": 15.50,
      "product_name": "Acetaminofén",
      "presentation_name": "Caja x100 tabletas",
      "lot_status": "ACTIVE"
    }
  ],
  "count": 1,
  "metadata": {
    "total_available_quantity": 75,
    "oldest_lot_date": "2024-01-15T10:30:00",
    "newest_lot_date": "2024-01-15T10:30:00"
  }
}
```

## ✅ Puntos Clave

| # | Punto Clave |
|---|-------------|
| 1 | **FIFO Automático**: Lotes ordenados por fecha de recepción |
| 2 | **Primera Posición = Más Antiguo**: Siempre usar `data[0]` |
| 3 | **Información Completa**: Producto + Presentación + Lote en una llamada |
| 4 | **lot_detail_id**: Campo `id` es el que se usa en conversión |
| 5 | **Metadata Útil**: Totales y rangos de fechas incluidos |

## 🚨 Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| 400 Bad Request | UUID inválido | Validar UUID antes de llamar |
| 404 Not Found | Sin lotes disponibles | Verificar que presentation tenga stock |
| 500 Internal Server Error | Error en BD | Revisar logs del servidor |

## 🔄 Flujo de Conversión

```
1. GET lot-details → Obtener lotes
2. data[0] → Seleccionar más antiguo (FIFO)
3. POST open-bulk → Convertir con lot_detail_id
4. ✅ Conversión completada
```

## 📚 Documentación

- **Guía Completa**: `LOT_DETAILS_ENDPOINT_GUIDE.md`
- **Resumen Ejecutivo**: `LOT_DETAILS_SUMMARY.md`
- **Guía de Conversión**: `BULK_CONVERSION_GUIDE.md`

## 🎯 Casos de Uso

1. ✅ **Conversión a granel** (principal)
2. ✅ Visualización de distribución de stock
3. ✅ Alertas de vencimiento
4. ✅ Análisis de rotación de inventario
5. ✅ Trazabilidad de lotes

---

**¿Necesitas ayuda?** Revisa `LOT_DETAILS_ENDPOINT_GUIDE.md` para ejemplos completos con TypeScript y React.
