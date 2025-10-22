# 🚀 Guía Rápida - Sistema de Reportes de Ventas

## Endpoints Disponibles

### 1. POST /reports/sales (Recomendado)
```bash
POST http://localhost:8000/reports/sales
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "period": "daily",          # "daily" | "weekly" | "monthly"
  "reference_date": "2025-10-21",
  "top_limit": 10             # Opcional, default: 10, max: 50
}
```

### 2. GET /reports/sales/quick/{period}
```bash
GET http://localhost:8000/reports/sales/quick/daily?reference_date=2025-10-21&top_limit=10
Authorization: Bearer YOUR_TOKEN
```

## Periodos

| Periodo | Descripción | Ejemplo |
|---------|-------------|---------|
| `daily` | Día completo 00:00 - 23:59 | 2025-10-21 → 2025-10-21 |
| `weekly` | Lunes a Domingo | 2025-10-21 (mar) → 2025-10-20 (lun) a 2025-10-26 (dom) |
| `monthly` | Mes completo | 2025-10-21 → 2025-10-01 a 2025-10-31 |

## Respuesta (Estructura)

```json
{
  "period": "daily",
  "start_date": "2025-10-21T00:00:00",
  "end_date": "2025-10-21T23:59:59.999999",
  
  // Métricas Generales
  "total_sales": 45,              // Número de ventas
  "total_revenue": 12450.50,      // Ingresos totales $
  "estimated_profit": 3890.75,    // Ganancia estimada $
  "profit_margin": 31.25,         // Margen %
  "average_sale_value": 276.68,   // Ticket promedio $
  "total_items_sold": 234,        // Items vendidos
  
  // Top Productos
  "top_products": [
    {
      "presentation_id": "uuid",
      "product_name": "Nombre del producto",
      "presentation_name": "Presentación",
      "total_quantity": 120,        // Unidades vendidas
      "total_revenue": 3000.00,     // Ingresos generados $
      "average_price": 25.00        // Precio promedio $
    }
  ],
  
  // Top Clientes
  "top_customers": [
    {
      "customer_id": "uuid",
      "customer_name": "Nombre Cliente",
      "customer_document": "CC: 1234567890",
      "total_purchases": 8,          // Número de compras
      "total_spent": 1250.00,        // Total gastado $
      "average_purchase": 156.25     // Promedio por compra $
    }
  ]
}
```

## Ejemplos Rápidos

### cURL - Reporte Diario
```bash
curl -X POST "http://localhost:8000/reports/sales" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"period":"daily","reference_date":"2025-10-21"}'
```

### cURL - Reporte Semanal
```bash
curl -X GET "http://localhost:8000/reports/sales/quick/weekly?reference_date=2025-10-21" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/reports/sales",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "period": "monthly",
        "reference_date": "2025-10-01",
        "top_limit": 20
    }
)

report = response.json()
print(f"Ganancia: ${report['estimated_profit']:,.2f}")
print(f"Margen: {report['profit_margin']}%")
```

### JavaScript
```javascript
const getReport = async (period, date) => {
  const res = await fetch('http://localhost:8000/reports/sales', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      period,
      reference_date: date,
      top_limit: 10
    })
  });
  return res.json();
};

// Uso
const report = await getReport('daily', '2025-10-21');
console.log('Ventas:', report.total_sales);
```

## Casos de Uso Comunes

### 1. Dashboard Diario
```json
POST /reports/sales
{
  "period": "daily",
  "reference_date": "2025-10-21",
  "top_limit": 5
}
```
**Para:** Ver resumen del día con top 5 productos y clientes

### 2. Análisis Semanal
```json
POST /reports/sales
{
  "period": "weekly",
  "reference_date": "2025-10-21",
  "top_limit": 15
}
```
**Para:** Planificación semanal e inventario

### 3. Cierre Mensual
```json
POST /reports/sales
{
  "period": "monthly",
  "reference_date": "2025-10-01",
  "top_limit": 20
}
```
**Para:** Reportes financieros y análisis de rentabilidad

## Fórmulas

```
Ganancia Estimada = Ingresos Totales - Costos Totales

Margen de Ganancia (%) = (Ganancia Estimada / Ingresos Totales) × 100

Ticket Promedio = Ingresos Totales / Número de Ventas
```

## Notas Importantes

✅ Requiere autenticación JWT
✅ Excluye ventas canceladas automáticamente
✅ Fecha en formato ISO: YYYY-MM-DD
✅ top_limit: mín 1, máx 50
✅ Horario: 00:00:00 a 23:59:59.999999

## Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| 401 Unauthorized | Token inválido/expirado | Renovar token de autenticación |
| 400 Bad Request | Periodo inválido | Usar: daily, weekly, monthly |
| 400 Bad Request | Fecha incorrecta | Formato: YYYY-MM-DD |
| 500 Internal Error | Error de BD | Revisar logs del servidor |

## Testing en Swagger

1. Ir a: `http://localhost:8000/docs`
2. Click en "Authorize" (candado)
3. Pegar token: `Bearer YOUR_TOKEN`
4. Navegar a `/reports/sales`
5. Click "Try it out"
6. Ingresar datos de prueba
7. Ejecutar

## Archivos Relacionados

- 📘 Documentación completa: `REPORTS_DOCUMENTATION.md`
- 📝 Resumen implementación: `REPORTS_IMPLEMENTATION_SUMMARY.md`
- 💻 Ejemplos de código: `examples/reports_usage_examples.py`
- 🧪 Tests: `tests/test_reports.py`

---

**¿Necesitas ayuda?** Consulta la documentación completa en `REPORTS_DOCUMENTATION.md`
