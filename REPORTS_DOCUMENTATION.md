# Documentación del Sistema de Reportes de Ventas

## Descripción General

El sistema de reportes permite generar análisis detallados de ventas con diferentes periodos (diario, semanal, mensual), incluyendo métricas de rendimiento, productos más vendidos y mejores clientes.

## Características Principales

### 1. **Periodos de Reporte**
- **Diario (`daily`)**: Reporte de un día específico
- **Semanal (`weekly`)**: Reporte de lunes a domingo de la semana que contiene la fecha de referencia
- **Mensual (`monthly`)**: Reporte del mes completo

### 2. **Métricas Incluidas**
- Número total de ventas
- Ingresos totales del periodo
- Ganancia estimada (ingresos - costos)
- Margen de ganancia (%)
- Valor promedio por venta
- Total de items vendidos

### 3. **Análisis Top**
- **Productos más vendidos**: Incluye cantidad vendida, ingresos generados y precio promedio
- **Mejores clientes**: Incluye número de compras, total gastado y promedio por compra

## Endpoints Disponibles

### 1. POST `/reports/sales`
Endpoint principal para generar reportes con body JSON.

**Request Body:**
```json
{
  "period": "daily",
  "reference_date": "2025-10-21",
  "top_limit": 10
}
```

**Parámetros:**
- `period` (requerido): Tipo de periodo - `"daily"`, `"weekly"`, o `"monthly"`
- `reference_date` (requerido): Fecha de referencia en formato `YYYY-MM-DD`
- `top_limit` (opcional): Número de items en tops (default: 10, min: 1, max: 50)

**Ejemplo de Respuesta:**
```json
{
  "period": "daily",
  "start_date": "2025-10-21T00:00:00",
  "end_date": "2025-10-21T23:59:59.999999",
  "total_sales": 45,
  "total_revenue": 12450.50,
  "estimated_profit": 3890.75,
  "profit_margin": 31.25,
  "average_sale_value": 276.68,
  "total_items_sold": 234,
  "top_products": [
    {
      "presentation_id": "uuid-presentacion",
      "product_name": "Arroz Diana",
      "presentation_name": "Paquete x 500g",
      "total_quantity": 120,
      "total_revenue": 3000.00,
      "average_price": 25.00
    }
  ],
  "top_customers": [
    {
      "customer_id": "uuid-cliente",
      "customer_name": "Juan Pérez",
      "customer_document": "CC: 1234567890",
      "total_purchases": 8,
      "total_spent": 1250.00,
      "average_purchase": 156.25
    }
  ]
}
```

### 2. GET `/reports/sales/quick/{period}`
Endpoint alternativo usando query parameters.

**URL:** `/reports/sales/quick/daily?reference_date=2025-10-21&top_limit=5`

**Parámetros:**
- `period` (path, requerido): `daily`, `weekly`, o `monthly`
- `reference_date` (query, requerido): Fecha en formato `YYYY-MM-DD`
- `top_limit` (query, opcional): Número de items en tops (default: 10)

## Casos de Uso

### Caso 1: Reporte Diario de Ventas
```bash
curl -X POST "http://localhost:8000/reports/sales" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "period": "daily",
    "reference_date": "2025-10-21",
    "top_limit": 10
  }'
```

**Uso:** Ver el rendimiento de ventas de un día específico, ideal para revisión diaria de operaciones.

### Caso 2: Reporte Semanal
```bash
curl -X POST "http://localhost:8000/reports/sales" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "period": "weekly",
    "reference_date": "2025-10-21",
    "top_limit": 15
  }'
```

**Uso:** Análisis semanal para identificar tendencias y planificar inventario.

### Caso 3: Reporte Mensual con Top 20
```bash
curl -X POST "http://localhost:8000/reports/sales" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "period": "monthly",
    "reference_date": "2025-10-01",
    "top_limit": 20
  }'
```

**Uso:** Reporte mensual completo para análisis financiero y estratégico.

### Caso 4: Endpoint Rápido (GET)
```bash
curl -X GET "http://localhost:8000/reports/sales/quick/daily?reference_date=2025-10-21&top_limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Uso:** Consulta rápida desde URL sin necesidad de body JSON.

## Lógica de Cálculo de Fechas

### Reporte Diario
- **Entrada:** `2025-10-21`
- **Periodo:** `2025-10-21 00:00:00` a `2025-10-21 23:59:59`

### Reporte Semanal
- **Entrada:** `2025-10-21` (martes)
- **Periodo:** `2025-10-20 00:00:00` (lunes) a `2025-10-26 23:59:59` (domingo)
- La semana siempre inicia en lunes y termina en domingo

### Reporte Mensual
- **Entrada:** `2025-10-21`
- **Periodo:** `2025-10-01 00:00:00` a `2025-10-31 23:59:59`
- El periodo cubre el mes completo de la fecha de referencia

## Cálculo de Métricas

### Ganancia Estimada
```
Ganancia Estimada = Ingresos Totales - Costos Totales
```
- **Ingresos Totales:** Suma de todas las ventas (`Sale.total`)
- **Costos Totales:** Suma de `cantidad × precio_costo` de cada item vendido

### Margen de Ganancia
```
Margen de Ganancia (%) = (Ganancia Estimada / Ingresos Totales) × 100
```

### Valor Promedio por Venta
```
Valor Promedio = Ingresos Totales / Número de Ventas
```

## Consideraciones Importantes

### 1. **Exclusión de Ventas Canceladas**
Todas las métricas excluyen automáticamente ventas con status `"cancelled"`.

### 2. **Precisión de Costos**
- Los costos se calculan desde `LotDetail.unit_cost` para productos empaquetados
- Si un producto se vendió desde granel sin cost_price directo, el costo puede ser 0

### 3. **Autenticación Requerida**
Todos los endpoints requieren autenticación JWT válida mediante el header:
```
Authorization: Bearer <token>
```

### 4. **Ordenamiento de Tops**
- **Top Productos:** Ordenados por cantidad total vendida (descendente)
- **Top Clientes:** Ordenados por total gastado (descendente)

## Estructura de Archivos Creados

```
backend/src/
├── schemas/
│   └── reports.py              # Esquemas Pydantic para requests/responses
├── services/
│   └── reports_service.py      # Lógica de negocio y cálculos
└── routers/
    └── reports.py              # Endpoints y validaciones
```

## Integración con Frontend

### Ejemplo en JavaScript/TypeScript
```javascript
// Generar reporte diario
const generateDailyReport = async (date) => {
  const response = await fetch('http://localhost:8000/reports/sales', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      period: 'daily',
      reference_date: date,
      top_limit: 10
    })
  });
  
  return await response.json();
};

// Uso
const report = await generateDailyReport('2025-10-21');
console.log(`Ventas: ${report.total_sales}`);
console.log(`Ingresos: $${report.total_revenue}`);
console.log(`Ganancia: $${report.estimated_profit}`);
```

### Ejemplo en Python
```python
import requests
from datetime import date

def get_sales_report(period: str, reference_date: date, token: str):
    url = "http://localhost:8000/reports/sales"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "period": period,
        "reference_date": reference_date.isoformat(),
        "top_limit": 10
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Uso
report = get_sales_report("weekly", date(2025, 10, 21), "your_token")
print(f"Ganancia estimada: ${report['estimated_profit']}")
print(f"Margen: {report['profit_margin']}%")
```

## Testing

### Prueba Manual con Swagger
1. Acceder a `http://localhost:8000/docs`
2. Autenticarse usando el botón "Authorize"
3. Navegar a la sección "reports"
4. Probar endpoint `POST /reports/sales`
5. Ingresar datos de prueba y ejecutar

### Prueba con cURL
```bash
# Reporte diario
curl -X POST "http://localhost:8000/reports/sales" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"period":"daily","reference_date":"2025-10-21","top_limit":5}'

# Reporte semanal (método GET)
curl -X GET "http://localhost:8000/reports/sales/quick/weekly?reference_date=2025-10-21" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Próximas Mejoras Sugeridas

1. **Exportación a PDF/Excel**: Añadir endpoints para exportar reportes
2. **Comparación de Periodos**: Comparar periodo actual vs anterior
3. **Gráficos y Visualizaciones**: Incluir datos para gráficos
4. **Filtros Adicionales**: Por categoría, vendedor, etc.
5. **Reportes Personalizados**: Rangos de fechas custom
6. **Cache de Reportes**: Cachear reportes frecuentes para mejor rendimiento
7. **Reportes Programados**: Sistema de generación automática

## Soporte

Para dudas o problemas:
- Revisar logs en `backend/logs/`
- Verificar que la base de datos tenga datos de ventas
- Confirmar autenticación Firebase configurada correctamente
