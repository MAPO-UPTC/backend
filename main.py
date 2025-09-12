import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models_db import Base
from database import engine
import firebase_admin
from firebase_admin import credentials

# Routers
from routers import user, product

# Inicializar Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

# Crear tablas automáticamente
Base.metadata.create_all(engine)

app = FastAPI(docs_url="/docs", title="MAPO Backend API")


# CORS configuration
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

# Include routers
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(product.router, prefix="/products", tags=["products"])

@app.get("/")
async def root():
    """
    Endpoint raíz de la API.
    """
    return {"message": "Welcome to MAPO Backend API"}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
