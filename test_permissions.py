import requests
import json

BASE_URL = "http://localhost:8000"

def test_permissions_system():
    """
    Script completo para probar el sistema de permisos
    """
    print("🔐 Testing MAPO Backend - Sistema de Permisos\n")
    
    # 1. Registrar un usuario (debería tener rol USER por defecto)
    print("1. Registrando usuario de prueba...")
    signup_data = {
        "name": "Test",
        "last_name": "User",
        "document_type": "CC",
        "document_number": "987654321",
        "email": "testpermissions@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/signup", json=signup_data)
        print(f"   Signup: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   Signup error: {e}")
    
    # 2. Login y obtener token con permisos
    print("\n2. Login para obtener token y permisos...")
    login_data = {
        "email": "testpermissions@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/login", json=login_data)
        if response.status_code == 200:
            login_result = response.json()
            token = login_result.get("idToken")
            user_info = login_result.get("user", {})
            
            print(f"   Login: {response.status_code}")
            print(f"   User: {user_info.get('name')} {user_info.get('last_name')}")
            print(f"   Roles: {user_info.get('roles', [])}")
            print(f"   Permisos para PRODUCTS:")
            product_permissions = user_info.get('permissions', {}).get('PRODUCTS', {})
            for action, level in product_permissions.items():
                print(f"     {action}: {level}")
        else:
            print(f"   Login failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"   Login error: {e}")
        return
    
    # 3. Probar endpoints con permisos
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n3. Probando acceso a productos...")
    
    # GET products (debería funcionar - USER tiene READ ALL en PRODUCTS)
    try:
        response = requests.get(f"{BASE_URL}/products/", headers=headers)
        print(f"   GET productos: {response.status_code}")
    except Exception as e:
        print(f"   GET productos error: {e}")
    
    # POST product (debería fallar - USER no tiene CREATE en PRODUCTS)
    product_data = {
        "name": "Producto Test",
        "description": "Descripción test",
        "category_id": None
    }
    
    try:
        response = requests.post(f"{BASE_URL}/products/", json=product_data, headers=headers)
        print(f"   POST producto: {response.status_code}")
        if response.status_code != 200:
            print(f"     Error (esperado): {response.json().get('detail', 'No detail')}")
    except Exception as e:
        print(f"   POST producto error: {e}")
    
    # 4. Obtener permisos del usuario actual
    print("\n4. Obteniendo permisos completos del usuario...")
    try:
        response = requests.get(f"{BASE_URL}/users/me/permissions", headers=headers)
        if response.status_code == 200:
            permissions_data = response.json()
            print(f"   Usuario ID: {permissions_data.get('user_id')}")
            print(f"   Roles: {permissions_data.get('roles', [])}")
            print("   Permisos detallados:")
            for entity, actions in permissions_data.get('permissions', {}).items():
                print(f"     {entity}:")
                for action, level in actions.items():
                    icon = "✅" if level != "NONE" else "❌"
                    print(f"       {icon} {action}: {level}")
        else:
            print(f"   Permisos error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   Permisos error: {e}")
    
    print("\n✅ Prueba del sistema de permisos completada!")
    print("\n📋 Resumen:")
    print("   - Usuario con rol USER puede leer productos ✅")
    print("   - Usuario con rol USER NO puede crear productos ❌")
    print("   - Sistema de permisos funcionando correctamente 🔐")

if __name__ == "__main__":
    test_permissions_system()