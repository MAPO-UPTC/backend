import uvicorn
import pyrebase as pyrebase
from fastapi import FastAPI
from models import SignUpSchema, LoginSchema
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from models_db import User
from sqlalchemy.orm import Session
from database import engine
from user.entities.user_entities import UserEntities
import jwt
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, auth as admin_auth

if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

app = FastAPI(docs_url="/docs")

SECRET_KEY = "TU_SECRETO_SUPER_SEGURO"


origins = [
    "http://localhost:3000",  # frontend React en desarrollo
    "http://127.0.0.1:3000",
    # En producción agregar tu dominio real
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permitir GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],  # Permitir headers como Authorization
)

firebaseConfig = {
    "apiKey": "AIzaSyDCyRrTCoKhf8Mdie8M45oPK2ViZIniK9I",
    "authDomain": "mapo-c59b6.firebaseapp.com",
    "projectId": "mapo-c59b6",
    "storageBucket": "mapo-c59b6.appspot.com",
    "messagingSenderId": "888526418042",
    "appId": "1:888526418042:web:07faf8987ffd17c13f0bc3",
    "measurementId": "G-ZFPK0K0DHW",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

@app.post("/signup")
async def create_an_account(user_data: SignUpSchema):
    print("Creating account for:", user_data)
    email = user_data.email
    password = user_data.password
    try:
        user = auth.create_user_with_email_and_password(email, password)
        print('localId')
        print(user['localId'])
        with Session(engine) as session:
            usertmp = session.query(User).filter_by(email=user_data.email).first()
            if not usertmp:
                db_user = User(
                    email=user_data.email,
                    first_name=user_data.first_name,
                    second_first_name=user_data.second_first_name,
                    last_name=user_data.last_name,
                    second_last_name=user_data.second_last_name,
                    phone_number=user_data.phone_number,
                    uid=user['localId'],
                )
                session.add(db_user)
                session.commit()
                session.refresh(db_user)
                return JSONResponse(content={"message": "User created successfully"})
    except Exception as e:
        print("Error al crear usuario en Firebase:", e)
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
async def create_access_token(user_data: LoginSchema):
    print("Attempting login...")
    email = user_data.email
    password = user_data.password
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return {"message": "Login successful", "idToken": user['idToken']}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid credentials")

@app.post("/ping")
async def validate_token(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        user = auth.get_account_info(token)
        return {"message": "Token is valid", "user": user}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/auth/google")
async def google_login(request: Request):
    body = await request.json()
    token = body.get("token")
    try:
        decoded_token = admin_auth.verify_id_token(token)
        email = decoded_token.get("email")
        print("Decoded token:", decoded_token.get("name", "").split(" "))
        print("Decoded token:", decoded_token)
        full_name = decoded_token.get("name", "")
        first_name, second_first_name, last_name, second_last_name = split_full_name(full_name)
        with Session(engine) as session:
            user = session.query(User).filter_by(email=email).first()
            if not user:
                user = User(
                    first_name=first_name,
                    second_first_name=second_first_name,
                    last_name=last_name,
                    second_last_name=second_last_name,
                    email=email,
                    uid=decoded_token.get("user_id"),
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            payload = {
                "user_id": str(user.id),
                "email": user.email,
                "exp": datetime.utcnow() + timedelta(hours=24)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            return {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "token": token
            }
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=401, detail="Token inválido")
    
@app.get("/users", response_model=list[UserEntities])
async def get_users():
    with Session(engine) as session:
        users = session.query(User).all()
        return users

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)


def split_full_name(full_name: str):
    # Divide y limpia cada parte
    parts = [p.replace("(", "").replace(")", "") for p in full_name.strip().split()]
    # Elimina partes vacías
    parts = [p for p in parts if p]
    first_name = parts[0] if len(parts) > 0 else ""
    second_first_name = parts[1] if len(parts) > 3 else None
    last_name = parts[-2] if len(parts) > 2 else (parts[1] if len(parts) == 2 else "")
    second_last_name = parts[-1] if len(parts) > 2 else None
    return first_name, second_first_name, last_name, second_last_name
