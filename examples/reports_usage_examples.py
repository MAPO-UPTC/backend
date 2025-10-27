"""
Ejemplos de uso del sistema de reportes de ventas

Este archivo contiene ejemplos prácticos de cómo utilizar los endpoints
de reportes desde diferentes clientes.
"""

# ============================================================================
# EJEMPLO 1: Python con requests
# ============================================================================

import requests
from datetime import date

def ejemplo_python_requests():
    """Ejemplo usando la librería requests de Python"""
    
    BASE_URL = "http://localhost:8000"
    TOKEN = "your_firebase_token_here"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Reporte diario
    print("=== REPORTE DIARIO ===")
    daily_data = {
        "period": "daily",
        "reference_date": "2025-10-21",
        "top_limit": 10
    }
    
    response = requests.post(
        f"{BASE_URL}/reports/sales",
        headers=headers,
        json=daily_data
    )
    
    if response.status_code == 200:
        report = response.json()
        print(f"Ventas totales: {report['total_sales']}")
        print(f"Ingresos: ${report['total_revenue']:.2f}")
        print(f"Ganancia: ${report['estimated_profit']:.2f}")
        print(f"Margen: {report['profit_margin']:.2f}%")
        
        print("\nTop 3 Productos:")
        for i, product in enumerate(report['top_products'][:3], 1):
            print(f"{i}. {product['product_name']} - {product['presentation_name']}")
            print(f"   Vendidos: {product['total_quantity']} - Ingresos: ${product['total_revenue']:.2f}")
        
        print("\nTop 3 Clientes:")
        for i, customer in enumerate(report['top_customers'][:3], 1):
            print(f"{i}. {customer['customer_name']}")
            print(f"   Compras: {customer['total_purchases']} - Total: ${customer['total_spent']:.2f}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # Reporte semanal usando GET
    print("\n=== REPORTE SEMANAL (GET) ===")
    response = requests.get(
        f"{BASE_URL}/reports/sales/quick/weekly",
        headers=headers,
        params={
            "reference_date": "2025-10-21",
            "top_limit": 5
        }
    )
    
    if response.status_code == 200:
        report = response.json()
        print(f"Periodo: {report['start_date']} a {report['end_date']}")
        print(f"Ventas de la semana: {report['total_sales']}")
        print(f"Ingresos semanales: ${report['total_revenue']:.2f}")


# ============================================================================
# EJEMPLO 2: JavaScript/TypeScript (Frontend)
# ============================================================================

"""
// Configuración
const BASE_URL = 'http://localhost:8000';
const token = 'your_firebase_token_here';

// Función para generar reporte
async function generateSalesReport(period, referenceDate, topLimit = 10) {
    try {
        const response = await fetch(`${BASE_URL}/reports/sales`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                period: period,
                reference_date: referenceDate,
                top_limit: topLimit
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error generating report:', error);
        throw error;
    }
}

// Uso: Reporte diario
generateSalesReport('daily', '2025-10-21')
    .then(report => {
        console.log('Total Sales:', report.total_sales);
        console.log('Revenue:', report.total_revenue);
        console.log('Profit:', report.estimated_profit);
        console.log('Margin:', report.profit_margin + '%');
        
        // Mostrar productos más vendidos
        console.log('\\nTop Products:');
        report.top_products.forEach((product, index) => {
            console.log(`${index + 1}. ${product.product_name} - ${product.presentation_name}`);
            console.log(`   Sold: ${product.total_quantity}, Revenue: $${product.total_revenue}`);
        });
    });

// Uso: Reporte semanal con método GET
async function getWeeklyReport(date) {
    const url = new URL(`${BASE_URL}/reports/sales/quick/weekly`);
    url.searchParams.append('reference_date', date);
    url.searchParams.append('top_limit', '15');
    
    const response = await fetch(url, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    return await response.json();
}

// React Component Example
function SalesReportComponent() {
    const [report, setReport] = React.useState(null);
    const [loading, setLoading] = React.useState(false);
    
    const loadDailyReport = async () => {
        setLoading(true);
        try {
            const today = new Date().toISOString().split('T')[0];
            const data = await generateSalesReport('daily', today, 10);
            setReport(data);
        } catch (error) {
            console.error('Failed to load report:', error);
        } finally {
            setLoading(false);
        }
    };
    
    React.useEffect(() => {
        loadDailyReport();
    }, []);
    
    if (loading) return <div>Cargando reporte...</div>;
    if (!report) return <div>No hay datos</div>;
    
    return (
        <div className="sales-report">
            <h2>Reporte de Ventas - {report.period}</h2>
            <div className="metrics">
                <div className="metric">
                    <h3>Ventas Totales</h3>
                    <p>{report.total_sales}</p>
                </div>
                <div className="metric">
                    <h3>Ingresos</h3>
                    <p>${report.total_revenue.toFixed(2)}</p>
                </div>
                <div className="metric">
                    <h3>Ganancia</h3>
                    <p>${report.estimated_profit.toFixed(2)}</p>
                </div>
                <div className="metric">
                    <h3>Margen</h3>
                    <p>{report.profit_margin}%</p>
                </div>
            </div>
            
            <div className="top-products">
                <h3>Productos Más Vendidos</h3>
                <ul>
                    {report.top_products.map((product, idx) => (
                        <li key={product.presentation_id}>
                            {idx + 1}. {product.product_name} - {product.presentation_name}
                            <br />
                            Cantidad: {product.total_quantity}, Ingresos: ${product.total_revenue}
                        </li>
                    ))}
                </ul>
            </div>
            
            <div className="top-customers">
                <h3>Mejores Clientes</h3>
                <ul>
                    {report.top_customers.map((customer, idx) => (
                        <li key={customer.customer_id}>
                            {idx + 1}. {customer.customer_name}
                            <br />
                            Compras: {customer.total_purchases}, Total: ${customer.total_spent}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}
"""


# ============================================================================
# EJEMPLO 3: cURL (Terminal/Postman)
# ============================================================================

"""
# Reporte Diario (POST)
curl -X POST "http://localhost:8000/reports/sales" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "period": "daily",
    "reference_date": "2025-10-21",
    "top_limit": 10
  }'

# Reporte Semanal (POST)
curl -X POST "http://localhost:8000/reports/sales" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "period": "weekly",
    "reference_date": "2025-10-21",
    "top_limit": 15
  }'

# Reporte Mensual (POST)
curl -X POST "http://localhost:8000/reports/sales" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "period": "monthly",
    "reference_date": "2025-10-01",
    "top_limit": 20
  }'

# Reporte Diario usando GET
curl -X GET "http://localhost:8000/reports/sales/quick/daily?reference_date=2025-10-21&top_limit=10" \\
  -H "Authorization: Bearer YOUR_TOKEN"

# Reporte Semanal usando GET
curl -X GET "http://localhost:8000/reports/sales/quick/weekly?reference_date=2025-10-21&top_limit=5" \\
  -H "Authorization: Bearer YOUR_TOKEN"
"""


# ============================================================================
# EJEMPLO 4: Procesamiento de Datos del Reporte
# ============================================================================

def procesar_reporte_para_dashboard(report_data):
    """
    Procesar datos del reporte para mostrar en un dashboard
    """
    
    # Métricas principales
    metricas = {
        'ventas_totales': report_data['total_sales'],
        'ingresos': f"${report_data['total_revenue']:,.2f}",
        'ganancia': f"${report_data['estimated_profit']:,.2f}",
        'margen': f"{report_data['profit_margin']:.2f}%",
        'ticket_promedio': f"${report_data['average_sale_value']:,.2f}",
        'items_vendidos': report_data['total_items_sold']
    }
    
    # Top 5 productos para gráfico
    productos_chart = {
        'labels': [p['product_name'] for p in report_data['top_products'][:5]],
        'quantities': [p['total_quantity'] for p in report_data['top_products'][:5]],
        'revenues': [p['total_revenue'] for p in report_data['top_products'][:5]]
    }
    
    # Top 5 clientes para tabla
    clientes_table = [
        {
            'nombre': c['customer_name'],
            'compras': c['total_purchases'],
            'total': f"${c['total_spent']:,.2f}",
            'promedio': f"${c['average_purchase']:,.2f}"
        }
        for c in report_data['top_customers'][:5]
    ]
    
    return {
        'metricas': metricas,
        'productos_chart': productos_chart,
        'clientes_table': clientes_table,
        'periodo': {
            'tipo': report_data['period'],
            'inicio': report_data['start_date'],
            'fin': report_data['end_date']
        }
    }


def comparar_periodos(report_actual, report_anterior):
    """
    Comparar dos reportes para mostrar tendencias
    """
    
    comparacion = {
        'ventas': {
            'actual': report_actual['total_sales'],
            'anterior': report_anterior['total_sales'],
            'cambio': report_actual['total_sales'] - report_anterior['total_sales'],
            'porcentaje': (
                ((report_actual['total_sales'] - report_anterior['total_sales']) 
                 / report_anterior['total_sales'] * 100)
                if report_anterior['total_sales'] > 0 else 0
            )
        },
        'ingresos': {
            'actual': report_actual['total_revenue'],
            'anterior': report_anterior['total_revenue'],
            'cambio': report_actual['total_revenue'] - report_anterior['total_revenue'],
            'porcentaje': (
                ((report_actual['total_revenue'] - report_anterior['total_revenue']) 
                 / report_anterior['total_revenue'] * 100)
                if report_anterior['total_revenue'] > 0 else 0
            )
        },
        'margen': {
            'actual': report_actual['profit_margin'],
            'anterior': report_anterior['profit_margin'],
            'cambio': report_actual['profit_margin'] - report_anterior['profit_margin']
        }
    }
    
    return comparacion


# ============================================================================
# EJEMPLO 5: Exportación de Datos
# ============================================================================

import csv
import json

def exportar_reporte_csv(report_data, filename="reporte_ventas.csv"):
    """
    Exportar productos más vendidos a CSV
    """
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Producto', 'Presentación', 'Cantidad', 'Ingresos', 'Precio Promedio']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for product in report_data['top_products']:
            writer.writerow({
                'Producto': product['product_name'],
                'Presentación': product['presentation_name'],
                'Cantidad': product['total_quantity'],
                'Ingresos': f"${product['total_revenue']:.2f}",
                'Precio Promedio': f"${product['average_price']:.2f}"
            })
    
    print(f"Reporte exportado a {filename}")


def exportar_reporte_json(report_data, filename="reporte_ventas.json"):
    """
    Exportar reporte completo a JSON
    """
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(report_data, jsonfile, indent=2, ensure_ascii=False, default=str)
    
    print(f"Reporte exportado a {filename}")


# ============================================================================
# EJEMPLO DE INTEGRACIÓN COMPLETA
# ============================================================================

def dashboard_completo():
    """
    Ejemplo de integración completa para un dashboard
    """
    import requests
    from datetime import date, timedelta
    
    BASE_URL = "http://localhost:8000"
    TOKEN = "your_token"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 1. Obtener reporte del día actual
    hoy = date.today()
    reporte_hoy = requests.post(
        f"{BASE_URL}/reports/sales",
        headers=headers,
        json={
            "period": "daily",
            "reference_date": hoy.isoformat(),
            "top_limit": 10
        }
    ).json()
    
    # 2. Obtener reporte de ayer para comparación
    ayer = hoy - timedelta(days=1)
    reporte_ayer = requests.post(
        f"{BASE_URL}/reports/sales",
        headers=headers,
        json={
            "period": "daily",
            "reference_date": ayer.isoformat(),
            "top_limit": 10
        }
    ).json()
    
    # 3. Obtener reporte semanal
    reporte_semana = requests.post(
        f"{BASE_URL}/reports/sales",
        headers=headers,
        json={
            "period": "weekly",
            "reference_date": hoy.isoformat(),
            "top_limit": 15
        }
    ).json()
    
    # 4. Procesar datos
    datos_dashboard = {
        'hoy': procesar_reporte_para_dashboard(reporte_hoy),
        'comparacion': comparar_periodos(reporte_hoy, reporte_ayer),
        'semana': procesar_reporte_para_dashboard(reporte_semana)
    }
    
    # 5. Mostrar resumen
    print("=== DASHBOARD DE VENTAS ===")
    print(f"\nVentas Hoy: {datos_dashboard['hoy']['metricas']['ventas_totales']}")
    print(f"Ingresos Hoy: {datos_dashboard['hoy']['metricas']['ingresos']}")
    print(f"Ganancia Hoy: {datos_dashboard['hoy']['metricas']['ganancia']}")
    print(f"\nCambio vs Ayer: {datos_dashboard['comparacion']['ventas']['cambio']:+d} ventas")
    print(f"                ({datos_dashboard['comparacion']['ventas']['porcentaje']:+.1f}%)")
    
    return datos_dashboard


if __name__ == "__main__":
    # Descomentar para probar
    # ejemplo_python_requests()
    # dashboard_completo()
    pass
