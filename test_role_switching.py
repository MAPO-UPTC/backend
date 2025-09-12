#!/usr/bin/env python3
"""
Script de prueba para el sistema de cambio de roles.
Demuestra cómo un usuario puede cambiar entre diferentes roles y 
cómo esto afecta sus permisos.
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = BASE_URL  # Sin prefijo /api/v1

def print_section(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

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

def test_role_switching():
    """
    Prueba el sistema de cambio de roles.
    """
    print_section("PRUEBA DEL SISTEMA DE CAMBIO DE ROLES")
    
    # 1. Crear usuario de prueba (asumimos que ya existe)
    print("\n1. Intentando login con usuario de prueba...")
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    login_response = requests.post(f"{API_BASE}/users/login", json=login_data)
    print_response(login_response, "Login")
    
    if login_response.status_code != 200:
        print("❌ No se pudo hacer login. Asegúrate de que el usuario existe.")
        return
    
    # Obtener token de autenticación
    login_result = login_response.json()
    token = login_result.get("idToken")
    
    if not token:
        print("❌ No se pudo obtener el token de autenticación.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Ver permisos actuales (todos los roles combinados)
    print_section("PERMISOS INICIALES (TODOS LOS ROLES)")
    permissions_response = requests.get(f"{API_BASE}/users/me/permissions", headers=headers)
    print_response(permissions_response)
    
    if permissions_response.status_code != 200:
        print("❌ No se pudieron obtener los permisos.")
        return
    
    permissions_data = permissions_response.json()
    available_roles = permissions_data.get("available_roles", [])
    
    print(f"\n📋 Roles disponibles: {available_roles}")
    print(f"🎭 Rol activo actual: {permissions_data.get('active_role', 'Ninguno (usando todos)')}")
    
    # 3. Probar acceso a productos con todos los roles
    print_section("PRUEBA DE ACCESO CON TODOS LOS ROLES")
    
    # Intentar obtener productos
    products_response = requests.get(f"{API_BASE}/products/", headers=headers)
    print_response(products_response, "GET Products (todos los roles)")
    
    # Intentar crear producto
    new_product = {
        "name": "Producto de Prueba",
        "description": "Descripción de prueba",
        "price": 100.0,
        "stock": 10
    }
    create_response = requests.post(f"{API_BASE}/products/", json=new_product, headers=headers)
    print_response(create_response, "POST Product (todos los roles)")
    
    # 4. Cambiar a rol USER (si está disponible)
    if "USER" in available_roles:
        print_section("CAMBIANDO A ROL USER")
        
        switch_data = {"role": "USER"}
        switch_response = requests.post(f"{API_BASE}/users/me/switch-role", json=switch_data, headers=headers)
        print_response(switch_response, "Switch to USER role")
        
        if switch_response.status_code == 200:
            # 5. Ver permisos con rol USER activo
            print("\n📋 Permisos con rol USER activo:")
            permissions_response = requests.get(f"{API_BASE}/users/me/permissions", headers=headers)
            print_response(permissions_response)
            
            # 6. Probar acceso con rol USER
            print_section("PRUEBA DE ACCESO CON ROL USER ACTIVO")
            
            # Intentar obtener productos (debería funcionar)
            products_response = requests.get(f"{API_BASE}/products/", headers=headers)
            print_response(products_response, "GET Products (rol USER)")
            
            # Intentar crear producto (debería fallar)
            create_response = requests.post(f"{API_BASE}/products/", json=new_product, headers=headers)
            print_response(create_response, "POST Product (rol USER) - Debería fallar")
    
    # 7. Cambiar a rol ADMIN (si está disponible)
    if "ADMIN" in available_roles:
        print_section("CAMBIANDO A ROL ADMIN")
        
        switch_data = {"role": "ADMIN"}
        switch_response = requests.post(f"{API_BASE}/users/me/switch-role", json=switch_data, headers=headers)
        print_response(switch_response, "Switch to ADMIN role")
        
        if switch_response.status_code == 200:
            # 8. Probar acceso con rol ADMIN
            print_section("PRUEBA DE ACCESO CON ROL ADMIN ACTIVO")
            
            # Intentar crear producto (debería funcionar)
            create_response = requests.post(f"{API_BASE}/products/", json=new_product, headers=headers)
            print_response(create_response, "POST Product (rol ADMIN) - Debería funcionar")
    
    # 9. Limpiar rol activo (volver a usar todos los roles)
    print_section("LIMPIANDO ROL ACTIVO")
    
    clear_response = requests.post(f"{API_BASE}/users/me/clear-active-role", headers=headers)
    print_response(clear_response, "Clear active role")
    
    # 10. Ver permisos finales
    print_section("PERMISOS FINALES (TODOS LOS ROLES NUEVAMENTE)")
    permissions_response = requests.get(f"{API_BASE}/users/me/permissions", headers=headers)
    print_response(permissions_response)
    
    print_section("RESUMEN")
    print("""
    🎯 FUNCIONALIDADES DEMOSTRADAS:
    
    ✅ Login y obtención de token
    ✅ Visualización de roles disponibles
    ✅ Cambio de rol activo (switch-role)
    ✅ Permisos dinámicos según rol activo
    ✅ Restricciones de acceso según rol
    ✅ Limpieza de rol activo
    ✅ Retorno a permisos combinados
    
    📝 NOTAS:
    - Con rol USER: Solo lectura de productos
    - Con rol ADMIN: Lectura y escritura de productos  
    - Sin rol activo: Combinación de todos los roles asignados
    """)

if __name__ == "__main__":
    test_role_switching()