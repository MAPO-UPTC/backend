"""
Tests para el sistema de reportes de ventas
"""

import pytest
from datetime import date, datetime, timedelta
from services.reports_service import get_date_range
from schemas.reports import ReportPeriod


class TestDateRangeCalculation:
    """Tests para cálculo de rangos de fechas"""
    
    def test_daily_range(self):
        """Test rango diario"""
        reference = date(2025, 10, 21)
        start, end = get_date_range(ReportPeriod.DAILY, reference)
        
        assert start.date() == reference
        assert end.date() == reference
        assert start.hour == 0 and start.minute == 0
        assert end.hour == 23 and end.minute == 59
    
    def test_weekly_range_monday(self):
        """Test rango semanal empezando en lunes"""
        reference = date(2025, 10, 20)  # Lunes
        start, end = get_date_range(ReportPeriod.WEEKLY, reference)
        
        # Debe empezar el mismo lunes
        assert start.date() == date(2025, 10, 20)
        # Debe terminar el domingo
        assert end.date() == date(2025, 10, 26)
    
    def test_weekly_range_wednesday(self):
        """Test rango semanal con fecha en mitad de semana"""
        reference = date(2025, 10, 22)  # Miércoles
        start, end = get_date_range(ReportPeriod.WEEKLY, reference)
        
        # Debe retroceder al lunes
        assert start.date() == date(2025, 10, 20)
        # Debe llegar hasta domingo
        assert end.date() == date(2025, 10, 26)
    
    def test_monthly_range_start(self):
        """Test rango mensual desde inicio de mes"""
        reference = date(2025, 10, 1)
        start, end = get_date_range(ReportPeriod.MONTHLY, reference)
        
        assert start.date() == date(2025, 10, 1)
        assert end.date() == date(2025, 10, 31)
    
    def test_monthly_range_mid(self):
        """Test rango mensual desde mitad de mes"""
        reference = date(2025, 10, 15)
        start, end = get_date_range(ReportPeriod.MONTHLY, reference)
        
        assert start.date() == date(2025, 10, 1)
        assert end.date() == date(2025, 10, 31)
    
    def test_monthly_range_february(self):
        """Test rango mensual para febrero"""
        reference = date(2025, 2, 15)
        start, end = get_date_range(ReportPeriod.MONTHLY, reference)
        
        assert start.date() == date(2025, 2, 1)
        assert end.date() == date(2025, 2, 28)  # 2025 no es bisiesto
    
    def test_monthly_range_december(self):
        """Test rango mensual para diciembre (cambio de año)"""
        reference = date(2025, 12, 15)
        start, end = get_date_range(ReportPeriod.MONTHLY, reference)
        
        assert start.date() == date(2025, 12, 1)
        assert end.date() == date(2025, 12, 31)


class TestReportValidation:
    """Tests para validación de reportes"""
    
    def test_invalid_period_raises_error(self):
        """Test que periodo inválido lanza error"""
        with pytest.raises(ValueError):
            get_date_range("invalid_period", date(2025, 10, 21))


# Casos de uso documentados
"""
CASOS DE USO PARA REPORTES

1. REPORTE DIARIO
   - Usuario: Gerente de tienda
   - Necesidad: Revisar ventas del día actual
   - Request: POST /reports/sales
     {
       "period": "daily",
       "reference_date": "2025-10-21",
       "top_limit": 10
     }
   - Resultado esperado:
     * Total de ventas del día
     * Ingresos y ganancias
     * Top 10 productos vendidos hoy
     * Top 10 clientes del día

2. REPORTE SEMANAL
   - Usuario: Administrador
   - Necesidad: Análisis semanal para planificación
   - Request: POST /reports/sales
     {
       "period": "weekly",
       "reference_date": "2025-10-21",
       "top_limit": 15
     }
   - Resultado esperado:
     * Ventas de lunes a domingo
     * Comparativa de productos más vendidos
     * Identificar mejores clientes de la semana

3. REPORTE MENSUAL
   - Usuario: Contador/Finanzas
   - Necesidad: Cierre mensual y análisis financiero
   - Request: POST /reports/sales
     {
       "period": "monthly",
       "reference_date": "2025-10-01",
       "top_limit": 20
     }
   - Resultado esperado:
     * Total de ventas del mes
     * Ganancia y margen mensual
     * Top 20 productos del mes
     * Top 20 clientes más valiosos

4. CONSULTA RÁPIDA (GET)
   - Usuario: Cualquier usuario autenticado
   - Necesidad: Consulta rápida desde navegador
   - Request: GET /reports/sales/quick/daily?reference_date=2025-10-21
   - Resultado esperado:
     * Mismo resultado que POST pero vía GET

EJEMPLOS DE RESPUESTA ESPERADA:

{
  "period": "daily",
  "start_date": "2025-10-21T00:00:00",
  "end_date": "2025-10-21T23:59:59.999999",
  "total_sales": 45,                    # 45 ventas en el día
  "total_revenue": 12450.50,            # $12,450.50 en ingresos
  "estimated_profit": 3890.75,          # $3,890.75 de ganancia
  "profit_margin": 31.25,               # 31.25% de margen
  "average_sale_value": 276.68,         # Promedio $276.68 por venta
  "total_items_sold": 234,              # 234 items vendidos
  "top_products": [
    {
      "presentation_id": "uuid-1",
      "product_name": "Arroz Diana",
      "presentation_name": "500g",
      "total_quantity": 120,            # 120 unidades vendidas
      "total_revenue": 3000.00,         # $3,000 en ingresos
      "average_price": 25.00            # Precio promedio $25
    }
  ],
  "top_customers": [
    {
      "customer_id": "uuid-1",
      "customer_name": "Juan Pérez",
      "customer_document": "CC: 1234567890",
      "total_purchases": 8,              # 8 compras
      "total_spent": 1250.00,            # $1,250 gastados
      "average_purchase": 156.25         # Promedio $156.25 por compra
    }
  ]
}
"""
