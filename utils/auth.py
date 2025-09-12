from fastapi import Depends, HTTPException, Request
from firebase_admin import auth as admin_auth

def get_current_user(request: Request):
    """
    Dependencia para validar el token de Firebase y obtener el usuario actual.
    """
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")
    
    # Extraer el token del header "Bearer <token>"
    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        # Si no hay espacio, asumir que es solo el token
        token = authorization
    
    try:
        decoded_token = admin_auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

def split_full_name(full_name: str):
    """
    Función para separar nombre completo en partes individuales.
    Maneja casos con paréntesis y nombres opcionales.
    """
    # Divide y limpia cada parte
    parts = [p.replace("(", "").replace(")", "") for p in full_name.strip().split()]
    # Elimina partes vacías
    parts = [p for p in parts if p]
    
    first_name = parts[0] if len(parts) > 0 else ""
    second_first_name = parts[1] if len(parts) > 3 else None
    last_name = parts[-2] if len(parts) > 2 else (parts[1] if len(parts) == 2 else "")
    second_last_name = parts[-1] if len(parts) > 2 else None
    
    return first_name, second_first_name, last_name, second_last_name