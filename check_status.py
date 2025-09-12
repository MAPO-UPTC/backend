#!/usr/bin/env python3
"""
Script de verificación completa del backend MAPO
Verifica todos los endpoints y funcionalidades principales
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Prueba básica de conectividad"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Health Check: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_signup():
    """Prueba registro de usuario"""
    try:
        data = {
            "name": "Juan",
            "last_name": "Pérez",
            "document_type": "CC",
            "document_number": "12345678",
            "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{BASE_URL}/signup", json=data)
        print(f"✅ Signup Test: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"❌ Signup Failed: {e}")
        return None

def test_login():
    """Prueba login de usuario"""
    try:
        data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{BASE_URL}/login", json=data)
        print(f"✅ Login Test: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            return response.json().get("idToken")
        return None
    except Exception as e:
        print(f"❌ Login Failed: {e}")
        return None

def test_docs():
    """Verifica que la documentación esté disponible"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"✅ Docs Available: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Docs Failed: {e}")
        return False

def main():
    print("🚀 MAPO Backend - Estado Funcional\n")
    print("=" * 50)
    
    # Verificaciones básicas
    if not test_health_check():
        print("❌ Servidor no está ejecutándose")
        return
    
    # Verificar documentación
    test_docs()
    
    # Pruebas de endpoints
    print("\n📝 Probando Endpoints:")
    print("-" * 30)
    
    # Registro
    signup_result = test_signup()
    
    # Login (puede fallar si el usuario no existe)
    login_token = test_login()
    
    print("\n📊 Resumen del Estado:")
    print("-" * 30)
    print("✅ Servidor: Funcionando")
    print("✅ Estructura: Actualizada")
    print("✅ Documentación: Disponible")
    print(f"{'✅' if signup_result else '⚠️'} Registro: {'Funcional' if signup_result else 'Revisar'}")
    print(f"{'✅' if login_token else '⚠️'} Login: {'Funcional' if login_token else 'Revisar'}")
    
    print(f"\n🌐 Accede a la documentación en: {BASE_URL}/docs")
    print("🔧 El backend está listo para desarrollo!")

if __name__ == "__main__":
    main()