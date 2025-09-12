import requests
import json

token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImVmMjQ4ZjQyZjc0YWUwZjk0OTIwYWY5YTlhMDEzMTdlZjJkMzVmZTEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vbWFwby1jNTliNiIsImF1ZCI6Im1hcG8tYzU5YjYiLCJhdXRoX3RpbWUiOjE3NTY2OTg5MDUsInVzZXJfaWQiOiIyYkZOT2NBSUExYllvUXJxZUxlNnZJWjdWa2YxIiwic3ViIjoiMmJGTk9jQUlBMWJZb1FycWVMZTZ2SVo3VmtmMSIsImlhdCI6MTc1NjY5ODkwNSwiZXhwIjoxNzU2NzAyNTA1LCJlbWFpbCI6ImRlYW0xMGh3QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJlbWFpbCI6WyJkZWFtMTBod0BnbWFpbC5jb20iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJwYXNzd29yZCJ9fQ.I-A-FT2VTfpujm3ZQLAOFxFV4D8jDCPLgcL9KaQycExTH0Tu3kc87oje8ruPwh-JR5a6dBD4YxL_H7Rpcq2cEh1-eRF4viLxMrqev2tw4qUbvA8-yMddRTrhDlp4xAXNNw0hsosqyTgUjQB0kJKmjZkO19xcEi3FKiODXrECfP3zFjDYr8iW7VOZew6uR-aHn9zLbWbwxDva-NAE6n4CjuspH9ekbeWkHRdjWrAfst5XvjUm1BvfIAjVfyoj62z3XFA1HhxQLPLkuxTEw_vLpUaVugNpr4M_NDyyQWSLby_LWYmV6oae8sOD1EqBdCO6fSeW3XBK1lTt51e2FHUjzw"

# Test para validar token de Firebase
def test_validate_token():
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        "http://localhost:8000/ping",
        headers=headers
    )
    print(f"Token validation: {response.status_code}")
    print(response.text)
    return response.text

# Test para registro de usuario
def test_signup():
    data = {
        "name": "Test",
        "last_name": "User",
        "document_type": "CC",
        "document_number": "1234567890",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post(
        "http://localhost:8000/signup",
        json=data
    )
    print(f"Signup test: {response.status_code}")
    print(response.json())
    return response.json()

# Test para login de usuario
def test_login():
    data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post(
        "http://localhost:8000/login",
        json=data
    )
    print(f"Login test: {response.status_code}")
    print(response.json())
    return response.json()

# Test para obtener usuarios (requiere autenticación)
def test_get_users():
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        "http://localhost:8000/users",
        headers=headers
    )
    print(f"Get users test: {response.status_code}")
    if response.status_code == 200:
        print(response.json())
    else:
        print(response.text)
    return response.json() if response.status_code == 200 else response.text

# Test para obtener un usuario específico
def test_get_user_by_id(user_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"http://localhost:8000/users/{user_id}",
        headers=headers
    )
    print(f"Get user by ID test: {response.status_code}")
    if response.status_code == 200:
        print(response.json())
    else:
        print(response.text)
    return response.json() if response.status_code == 200 else response.text

# Test para actualizar usuario
def test_update_user(user_id):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "email": "updated@example.com",
        "person": {
            "name": "Updated",
            "last_name": "Name",
            "document_type": "TI",
            "document_number": "9876543210"
        }
    }
    response = requests.put(
        f"http://localhost:8000/users/{user_id}",
        json=data,
        headers=headers
    )
    print(f"Update user test: {response.status_code}")
    if response.status_code == 200:
        print(response.json())
    else:
        print(response.text)
    return response.json() if response.status_code == 200 else response.text

# Test para productos (endpoints mock)
def test_get_products():
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        "http://localhost:8000/products",
        headers=headers
    )
    print(f"Get products test: {response.status_code}")
    print(response.json())
    return response.json()

def test_create_product():
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "Test Product",
        "description": "A test product",
        "price": 29.99
    }
    response = requests.post(
        "http://localhost:8000/products",
        json=data,
        headers=headers
    )
    print(f"Create product test: {response.status_code}")
    print(response.json())
    return response.json()

# Ejecutar tests
if __name__ == "__main__":
    print("=== Testing MAPO Backend ===\n")
    
    print("1. Testing signup...")
    # test_signup()
    
    print("\n2. Testing login...")
    # test_login()
    
    print("\n3. Testing token validation...")
    # test_validate_token()
    
    print("\n4. Testing get users...")
    test_get_users()
    
    print("\n5. Testing get products...")
    test_get_products()
    
    print("\n6. Testing create product...")
    test_create_product()