# Script de prueba para el endpoint de detalles de venta

import sys
sys.path.append('src')

from database import SessionLocal
from services.sales_service import get_sale_full_details, get_sales

def test_sale_details():
    """
    Script para probar el endpoint de detalles de venta
    """
    db = SessionLocal()
    
    try:
        print("🔍 Buscando ventas en la base de datos...\n")
        
        # Obtener las últimas 5 ventas
        sales = get_sales(db, skip=0, limit=5)
        
        if not sales:
            print("❌ No hay ventas en la base de datos")
            print("   Crea una venta primero usando POST /sales/")
            return
        
        print(f"✅ Se encontraron {len(sales)} ventas\n")
        print("=" * 80)
        
        # Mostrar detalles de la primera venta
        first_sale = sales[0]
        print(f"\n📋 Probando detalles de la venta: {first_sale.sale_code}")
        print(f"   ID: {first_sale.id}")
        print(f"   Fecha: {first_sale.sale_date}")
        print(f"   Total: ${first_sale.total:.2f}")
        print("\n" + "=" * 80)
        
        # Obtener detalles completos
        details = get_sale_full_details(db, str(first_sale.id))
        
        if not details:
            print("❌ Error: No se pudieron obtener los detalles")
            return
        
        print("\n✅ DETALLES COMPLETOS DE LA VENTA\n")
        print("=" * 80)
        
        # Información general
        print(f"\n📌 INFORMACIÓN GENERAL")
        print(f"   Código: {details['sale_code']}")
        print(f"   Fecha: {details['sale_date']}")
        print(f"   Estado: {details['status']}")
        print(f"   Total: ${details['total']:.2f}")
        
        # Información del cliente
        print(f"\n👤 CLIENTE")
        print(f"   Nombre: {details['customer_name']}")
        print(f"   Documento: {details['customer_document']}")
        
        # Información del vendedor
        print(f"\n👨‍💼 VENDEDOR")
        print(f"   Nombre: {details['seller_name']}")
        
        # Items
        print(f"\n📦 PRODUCTOS VENDIDOS ({len(details['items'])} items)")
        print("=" * 80)
        
        total_cost = 0
        total_profit = 0
        
        for i, item in enumerate(details['items'], 1):
            item_cost = item['cost_price'] * item['quantity']
            item_profit = item['line_total'] - item_cost
            item_margin = (item_profit / item['line_total'] * 100) if item['line_total'] > 0 else 0
            
            total_cost += item_cost
            total_profit += item_profit
            
            tipo = "🌾 Granel" if item['bulk_conversion_id'] else "📦 Empaquetado"
            
            print(f"\nItem {i}: {item['product_name']}")
            print(f"   Presentación: {item['presentation_name']} {tipo}")
            print(f"   Cantidad: {item['quantity']}")
            print(f"   Precio Costo: ${item['cost_price']:.2f}")
            print(f"   Precio Venta: ${item['unit_price']:.2f}")
            print(f"   Subtotal: ${item['line_total']:.2f}")
            print(f"   Ganancia: ${item_profit:.2f} ({item_margin:.1f}%)")
        
        # Resumen financiero
        print("\n" + "=" * 80)
        print("\n💰 RESUMEN FINANCIERO")
        print(f"   Costo Total: ${total_cost:.2f}")
        print(f"   Total Venta: ${details['total']:.2f}")
        print(f"   Ganancia: ${total_profit:.2f}")
        
        if details['total'] > 0:
            margin = (total_profit / details['total'] * 100)
            print(f"   Margen: {margin:.2f}%")
        
        print("\n" + "=" * 80)
        print("\n✅ Endpoint funcionando correctamente!")
        print(f"\n🔗 Prueba en Swagger: http://localhost:8000/docs")
        print(f"   Endpoint: GET /sales/{first_sale.id}/details")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" 🧪 TEST: Endpoint de Detalles de Venta")
    print("=" * 80 + "\n")
    
    test_sale_details()
    
    print("\n" + "=" * 80)
    print(" Fin del test")
    print("=" * 80 + "\n")
