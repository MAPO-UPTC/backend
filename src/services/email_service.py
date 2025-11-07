"""
Servicio para envío de correos electrónicos
"""

import os
import random
import smtplib
import string
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from fastapi import HTTPException

# Almacenamiento temporal de códigos de reset (en producción usar Redis o base de datos)
# Estructura: {email: {"code": "123456", "expires_at": datetime, "attempts": 0}}
PASSWORD_RESET_CODES = {}

# Configuración desde variables de entorno
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USERNAME)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "MAPO Sistema")

# Configuración de seguridad
MAX_RESET_ATTEMPTS = 3
CODE_EXPIRATION_MINUTES = 15


def generate_reset_code(length: int = 6) -> str:
    """
    Generar un código aleatorio de 6 dígitos
    """
    return "".join(random.choices(string.digits, k=length))


def store_reset_code(email: str, code: str) -> None:
    """
    Almacenar código de reset con tiempo de expiración
    """
    expires_at = datetime.now() + timedelta(minutes=CODE_EXPIRATION_MINUTES)
    PASSWORD_RESET_CODES[email] = {
        "code": code,
        "expires_at": expires_at,
        "attempts": 0,
    }


def validate_reset_code(email: str, code: str) -> bool:
    """
    Validar código de reset
    """
    if email not in PASSWORD_RESET_CODES:
        raise HTTPException(
            status_code=400, detail="No se ha solicitado cambio de contraseña para este email"
        )

    stored_data = PASSWORD_RESET_CODES[email]

    # Verificar expiración
    if datetime.now() > stored_data["expires_at"]:
        del PASSWORD_RESET_CODES[email]
        raise HTTPException(
            status_code=400, detail="El código de recuperación ha expirado. Solicite uno nuevo."
        )

    # Verificar intentos
    if stored_data["attempts"] >= MAX_RESET_ATTEMPTS:
        del PASSWORD_RESET_CODES[email]
        raise HTTPException(
            status_code=400,
            detail="Demasiados intentos fallidos. Solicite un nuevo código.",
        )

    # Validar código
    if stored_data["code"] != code:
        stored_data["attempts"] += 1
        raise HTTPException(status_code=400, detail="Código de recuperación inválido")

    return True


def clear_reset_code(email: str) -> None:
    """
    Limpiar código de reset después de uso exitoso
    """
    if email in PASSWORD_RESET_CODES:
        del PASSWORD_RESET_CODES[email]


def send_email(to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> bool:
    """
    Enviar correo electrónico usando SMTP
    """
    # Verificar configuración
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("⚠️ SMTP no configurado. Email no enviado (modo desarrollo).")
        print(f"📧 Email que se enviaría a: {to_email}")
        print(f"📝 Asunto: {subject}")
        print(f"📄 Cuerpo:\n{text_body or html_body}")
        return True  # En desarrollo, simular envío exitoso

    try:
        # Crear mensaje
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        # Agregar cuerpo de texto plano y HTML
        if text_body:
            msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        # Conectar y enviar
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"✅ Email enviado exitosamente a: {to_email}")
        return True

    except Exception as e:
        print(f"❌ Error enviando email: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error enviando correo electrónico: {str(e)}",
        )


def send_password_reset_email(to_email: str, reset_code: str) -> bool:
    """
    Enviar correo de recuperación de contraseña
    """
    subject = "Recuperación de Contraseña - MAPO Sistema"

    # Cuerpo en texto plano
    text_body = f"""
Hola,

Has solicitado restablecer tu contraseña en MAPO Sistema.

Tu código de recuperación es: {reset_code}

Este código es válido por {CODE_EXPIRATION_MINUTES} minutos.

Si no solicitaste este cambio, ignora este correo.

Saludos,
Equipo MAPO
    """

    # Cuerpo en HTML
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .header {{
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: white;
            padding: 30px;
            border-radius: 0 0 5px 5px;
        }}
        .code {{
            font-size: 32px;
            font-weight: bold;
            color: #4CAF50;
            text-align: center;
            padding: 20px;
            background-color: #f0f0f0;
            border-radius: 5px;
            letter-spacing: 5px;
            margin: 20px 0;
        }}
        .warning {{
            color: #666;
            font-size: 12px;
            text-align: center;
            margin-top: 20px;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Recuperación de Contraseña</h1>
        </div>
        <div class="content">
            <p>Hola,</p>
            <p>Has solicitado restablecer tu contraseña en <strong>MAPO Sistema</strong>.</p>
            <p>Tu código de recuperación es:</p>
            <div class="code">{reset_code}</div>
            <p>Este código es válido por <strong>{CODE_EXPIRATION_MINUTES} minutos</strong>.</p>
            <p>Si no solicitaste este cambio, puedes ignorar este correo de forma segura.</p>
            <div class="warning">
                Por tu seguridad, nunca compartas este código con nadie.
            </div>
        </div>
        <div class="footer">
            <p>Saludos,<br>Equipo MAPO</p>
        </div>
    </div>
</body>
</html>
    """

    return send_email(to_email, subject, html_body, text_body)
