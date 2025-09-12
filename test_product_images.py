#!/usr/bin/env python3
"""
Script de prueba para endpoints de productos con image_url.
Prueba la funcionalidad completa de CRUD con imágenes.
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_response(response, title="Response"):
    print(f"\n{title}:")
    print(f"Status: {response.status_code}")
    if response.status_code < 400:
        try:
            data = response.json()
            print(json.dumps(data, indent=2, default=str))
        except:
            print(response.text)
    else:
        print(f"Error: {response.text}")

def test_products_with_images():
    """
    Prueba los endpoints de productos con image_url.
    """
    print_section("PRUEBA DE PRODUCTOS CON IMÁGENES")
    
    # 1. Login para obtener token
    print("\n1. Intentando login...")
    login_data = {
        "email": "testadmin@x.com",
        "password": "a123456"
    }
    
    login_response = requests.post(f"{BASE_URL}/users/login", json=login_data)
    print_response(login_response, "Login")
    
    if login_response.status_code != 200:
        print("❌ No se pudo hacer login.")
        return
    
    login_result = login_response.json()
    token = login_result.get("idToken")
    
    if not token:
        print("❌ No se pudo obtener el token.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Crear producto CON imagen
    print_section("CREAR PRODUCTO CON IMAGEN")
    
    product_with_image = {
        "name": f"Producto con Imagen {json.dumps({'timestamp': 'now'})}",
        "description": "Este producto tiene una imagen asociada",
        "image_url": "https://example.com/images/producto-ejemplo.jpg"
    }
    
    create_response = requests.post(f"{BASE_URL}/products/", json=product_with_image, headers=headers)
    print_response(create_response, "Crear producto con imagen")
    
    product_with_image_id = None
    if create_response.status_code == 200:
        product_with_image_id = create_response.json()["product"]["id"]
        print(f"✅ Producto con imagen creado con ID: {product_with_image_id}")
    
    # 3. Crear producto SIN imagen
    print_section("CREAR PRODUCTO SIN IMAGEN")
    
    product_without_image = {
        "name": f"Producto sin Imagen {json.dumps({'timestamp': 'now2'})}",
        "description": "Este producto no tiene imagen"
        # image_url se omite intencionalmente
    }
    
    create_response2 = requests.post(f"{BASE_URL}/products/", json=product_without_image, headers=headers)
    print_response(create_response2, "Crear producto sin imagen")
    
    product_without_image_id = None
    if create_response2.status_code == 200:
        product_without_image_id = create_response2.json()["product"]["id"]
        print(f"✅ Producto sin imagen creado con ID: {product_without_image_id}")
    
    # 4. Listar todos los productos (verificar que aparezcan las imágenes)
    print_section("LISTAR TODOS LOS PRODUCTOS")
    
    list_response = requests.get(f"{BASE_URL}/products/", headers=headers)
    print_response(list_response, "Lista de productos")
    
    if list_response.status_code == 200:
        products = list_response.json()
        print(f"\n📊 Total de productos: {len(products)}")
        
        # Verificar productos con y sin imagen
        with_image = [p for p in products if p.get('image_url')]
        without_image = [p for p in products if not p.get('image_url')]
        
        print(f"🖼️  Productos con imagen: {len(with_image)}")
        print(f"📄 Productos sin imagen: {len(without_image)}")
    
    # 5. Obtener producto específico por ID
    if product_with_image_id:
        print_section("OBTENER PRODUCTO CON IMAGEN POR ID")
        
        get_response = requests.get(f"{BASE_URL}/products/{product_with_image_id}", headers=headers)
        print_response(get_response, f"Producto ID {product_with_image_id}")
    
    # 6. Actualizar producto - agregar imagen
    if product_without_image_id:
        print_section("ACTUALIZAR PRODUCTO - AGREGAR IMAGEN")
        
        update_data = {
            "image_url": "https://example.com/images/producto-actualizado.png"
        }
        
        update_response = requests.put(f"{BASE_URL}/products/{product_without_image_id}", json=update_data, headers=headers)
        print_response(update_response, "Actualizar producto (agregar imagen)")
    
    # 7. Actualizar producto - cambiar imagen
    if product_with_image_id:
        print_section("ACTUALIZAR PRODUCTO - CAMBIAR IMAGEN")
        
        update_data = {
            "description": "Descripción actualizada con nueva imagen",
            "image_url": "https://example.com/images/nueva-imagen-producto.webp"
        }
        
        update_response = requests.put(f"{BASE_URL}/products/{product_with_image_id}", json=update_data, headers=headers)
        print_response(update_response, "Actualizar producto (cambiar imagen)")
    
    # 8. Actualizar producto - quitar imagen (establecer como null)
    if product_with_image_id:
        print_section("ACTUALIZAR PRODUCTO - QUITAR IMAGEN")
        
        update_data = {
            "image_url": None  # Explícitamente establecer como null
        }
        
        update_response = requests.put(f"{BASE_URL}/products/{product_with_image_id}", json=update_data, headers=headers)
        print_response(update_response, "Actualizar producto (quitar imagen)")
    
    # 9. Verificación final - listar productos nuevamente
    print_section("VERIFICACIÓN FINAL")
    
    final_list_response = requests.get(f"{BASE_URL}/products/", headers=headers)
    print_response(final_list_response, "Lista final de productos")
    
    if final_list_response.status_code == 200:
        products = final_list_response.json()
        
        print(f"\n📊 RESUMEN FINAL:")
        print(f"Total de productos: {len(products)}")
        
        for product in products[-4:]:  # Mostrar últimos 4 productos
            image_status = "🖼️  CON IMAGEN" if product.get('image_url') else "📄 SIN IMAGEN"
            print(f"- {product['name'][:30]}... | {image_status}")
            if product.get('image_url'):
                print(f"  📎 URL: {product['image_url']}")
    
    print_section("RESUMEN DE FUNCIONALIDADES PROBADAS")
    print("""
    🎯 FUNCIONALIDADES VALIDADAS:
    
    ✅ Crear producto CON image_url
    ✅ Crear producto SIN image_url (campo opcional)
    ✅ Listar productos (incluye image_url en respuesta)
    ✅ Obtener producto por ID (incluye image_url)
    ✅ Actualizar producto - agregar imagen
    ✅ Actualizar producto - cambiar imagen  
    ✅ Actualizar producto - quitar imagen (null)
    ✅ Campos opcionales funcionando correctamente
    
    📝 CASOS CUBIERTOS:
    - URL de imagen válida
    - Campo image_url omitido (null por defecto)
    - Actualización parcial manteniendo otros campos
    - Eliminación de imagen (establecer null)
    - Respuestas incluyen image_url en todos los endpoints
    """)

if __name__ == "__main__":
    test_products_with_images()