#!/usr/bin/env python3
"""
Script de prueba específico para probar el establecimiento de image_url como null.
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"

def test_null_image_url():
    """
    Prueba específica para establecer image_url como null.
    """
    print("🧪 PRUEBA: Establecer image_url como NULL")
    
    # 1. Login
    login_data = {
        "email": "testadmin@x.com",
        "password": "a123456"
    }
    
    login_response = requests.post(f"{BASE_URL}/users/login", json=login_data)
    if login_response.status_code != 200:
        print("❌ Error en login")
        return
    
    token = login_response.json().get("idToken")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Crear producto con imagen
    print("\n1. Creando producto con imagen...")
    product_data = {
        "name": "Producto para Prueba NULL",
        "description": "Este producto tendrá su imagen removida",
        "image_url": "https://example.com/imagen-inicial.jpg"
    }
    
    create_response = requests.post(f"{BASE_URL}/products/", json=product_data, headers=headers)
    if create_response.status_code != 200:
        print("❌ Error creando producto")
        return
    
    product_id = create_response.json()["product"]["id"]
    print(f"✅ Producto creado con ID: {product_id}")
    print(f"📎 Imagen inicial: {create_response.json()['product']['image_url']}")
    
    # 3. Actualizar para establecer image_url como null
    print("\n2. Estableciendo image_url como NULL...")
    update_data = {
        "image_url": None
    }
    
    update_response = requests.put(f"{BASE_URL}/products/{product_id}", json=update_data, headers=headers)
    
    print(f"Status de actualización: {update_response.status_code}")
    if update_response.status_code == 200:
        updated_product = update_response.json()["product"]
        print(f"✅ Producto actualizado")
        print(f"📎 Imagen después: {updated_product['image_url']}")
        
        if updated_product['image_url'] is None:
            print("🎉 ¡ÉXITO! La imagen se estableció correctamente como NULL")
        else:
            print(f"❌ ERROR: La imagen no se estableció como NULL, valor actual: {updated_product['image_url']}")
    else:
        print(f"❌ Error actualizando: {update_response.text}")
    
    # 4. Verificar consultando el producto
    print("\n3. Verificando consulta del producto...")
    get_response = requests.get(f"{BASE_URL}/products/{product_id}", headers=headers)
    
    if get_response.status_code == 200:
        product = get_response.json()
        print(f"📎 Imagen en consulta: {product['image_url']}")
        
        if product['image_url'] is None:
            print("✅ Confirmado: La imagen está NULL en la base de datos")
        else:
            print(f"❌ Problema: La imagen no es NULL: {product['image_url']}")

if __name__ == "__main__":
    test_null_image_url()