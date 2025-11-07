# 📧 Guía de Configuración de Email (SMTP)

## 🤔 ¿Qué significa "tu-email@gmail.com"?

Es un **placeholder** (marcador de posición) que debes **reemplazar** con tu correo electrónico real.

### ❌ Incorrecto:
```bash
SMTP_USERNAME=tu-email@gmail.com  # NO uses esto literalmente
```

### ✅ Correcto:
```bash
SMTP_USERNAME=tucorreo@gmail.com  # Reemplaza con tu correo real
```

---

## 📍 ¿Dónde va la configuración?

La configuración va en el archivo **`.env`** que está en:
```
c:\Users\Usuario\Documents\MAPO_Backend\backend\.env
```

---

## Configuración de Email SMTP y Firebase para Reset de Contraseña

### **Paso 1: Preparar tu cuenta de Gmail**

1. Ve a tu cuenta de Gmail
2. Habilita la **Verificación en 2 pasos** (requisito obligatorio)
   - Ve a: https://myaccount.google.com/security
   - Busca "Verificación en 2 pasos" y actívala

### **Paso 2: Generar Contraseña de Aplicación**

1. Ve a: https://myaccount.google.com/apppasswords
2. En "Seleccionar app" → Elige "Correo"
3. En "Seleccionar dispositivo" → Elige "Otro" y escribe "MAPO Backend"
4. Haz clic en **"Generar"**
5. Google te mostrará una contraseña de 16 caracteres, algo así:
   ```
   abcd efgh ijkl mnop
   ```
6. **¡Cópiala!** (solo se muestra una vez)

### **Paso 3: Configurar el archivo .env**

Abre el archivo `.env` y busca la sección de SMTP. Reemplaza con tus datos:

```bash
# ANTES (ejemplo con placeholders)
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=

# DESPUÉS (con tus datos reales)
SMTP_USERNAME=tucorreo@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
SMTP_FROM_EMAIL=tucorreo@gmail.com
```

### **Ejemplo Completo Real:**

Si tu correo es `maposistema@gmail.com` y tu contraseña de app es `wxyz abcd efgh ijkl`:

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=maposistema@gmail.com
SMTP_PASSWORD=wxyzabcdefghijkl
SMTP_FROM_EMAIL=maposistema@gmail.com
SMTP_FROM_NAME=MAPO Sistema
```

⚠️ **IMPORTANTE**: La contraseña NO lleva espacios en el .env

---

## 🔥 IMPORTANTE: Configuración de Firebase Service Account

**⚠️ PROBLEMA ACTUAL:** El `FIREBASE_CLIENT_EMAIL` en el `.env` está configurado con un email personal en lugar de las credenciales del Service Account de Firebase.

### ❌ Configuración INCORRECTA (actual):
```bash
FIREBASE_CLIENT_EMAIL=deam10hw@gmail.com  # Email personal ❌
```

### ✅ Configuración CORRECTA:
```bash
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@mapo-c59b6.iam.gserviceaccount.com
```

---

### 🔧 Cómo obtener las credenciales correctas de Firebase:

#### **Paso 1: Ir a Firebase Console**
1. Ve a: https://console.firebase.google.com/
2. Selecciona tu proyecto **`mapo-c59b6`**

#### **Paso 2: Acceder a Service Accounts**
1. Haz clic en el **⚙️ (engranaje)** junto a "Project Overview"
2. Selecciona **"Project settings"**
3. Ve a la pestaña **"Service accounts"**

#### **Paso 3: Generar nueva clave privada**
1. Haz clic en el botón **"Generate new private key"**
2. Confirma en el diálogo que aparece
3. Se descargará un archivo JSON con un nombre como:
   ```
   mapo-c59b6-firebase-adminsdk-xxxxx-abc123.json
   ```

#### **Paso 4: Abrir el archivo JSON**
El archivo JSON descargado tiene este formato:
```json
{
  "type": "service_account",
  "project_id": "mapo-c59b6",
  "private_key_id": "abc123def456...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBg...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@mapo-c59b6.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

#### **Paso 5: Actualizar el archivo `.env`**

Copia los siguientes valores del JSON al `.env`:

```bash
# Firebase Service Account (Copiar del JSON descargado)
FIREBASE_TYPE="service_account"
FIREBASE_PROJECT_ID="mapo-c59b6"
FIREBASE_PRIVATE_KEY_ID="abc123def456..."
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBg...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL="firebase-adminsdk-xxxxx@mapo-c59b6.iam.gserviceaccount.com"
FIREBASE_CLIENT_ID="123456789012345678901"
FIREBASE_AUTH_URI="https://accounts.google.com/o/oauth2/auth"
FIREBASE_TOKEN_URI="https://oauth2.googleapis.com/token"
FIREBASE_AUTH_PROVIDER_X509_CERT_URL="https://www.googleapis.com/oauth2/v1/certs"
FIREBASE_CLIENT_X509_CERT_URL="https://www.googleapis.com/robot/v1/metadata/x509/..."
```

**⚠️ IMPORTANTE PARA `FIREBASE_PRIVATE_KEY`:**
- Mantén los saltos de línea como `\n`
- Asegúrate de incluir las comillas
- El valor debe empezar con `"-----BEGIN PRIVATE KEY-----\n` y terminar con `\n-----END PRIVATE KEY-----\n"`

#### **Ejemplo de formato correcto para PRIVATE_KEY:**
```bash
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n...\n-----END PRIVATE KEY-----\n"
```

---

### 🧪 Verificar la configuración de Firebase:

Después de actualizar el `.env`, verifica que Firebase se inicialice correctamente:

```powershell
# Desde PowerShell en la carpeta backend/
python -c "import firebase_admin; from firebase_admin import credentials; print('Firebase OK' if firebase_admin._apps else 'Firebase NO inicializado')"
```

Si todo está bien, deberías ver:
```
Firebase OK
```

---

## 🧪 Probar la Configuración

### **1. Sin configurar (Modo Desarrollo)**

Si dejas las variables vacías, el sistema funcionará pero **no enviará emails reales**.
En su lugar, imprimirá el código en la consola:

```
⚠️ SMTP no configurado. Email no enviado (modo desarrollo).
📧 Email que se enviaría a: usuario@ejemplo.com
📝 Asunto: Recuperación de Contraseña
📄 Cuerpo:
Tu código de recuperación es: 123456
```

### **2. Con configuración (Modo Producción)**

Con SMTP configurado, se enviarán emails reales.

### **3. Probar el endpoint:**

```bash
# Solicitar código de recuperación
curl -X POST http://localhost:8000/users/request-password-reset \
  -H "Content-Type: application/json" \
  -d '{"email": "usuario@ejemplo.com"}'

# Revisa tu consola (sin SMTP) o tu email (con SMTP)
# Deberías recibir un código de 6 dígitos
```

---

## 📋 Resumen de Variables

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SMTP_SERVER` | Servidor de correo | `smtp.gmail.com` |
| `SMTP_PORT` | Puerto del servidor | `587` |
| `SMTP_USERNAME` | Tu correo electrónico | `tucorreo@gmail.com` |
| `SMTP_PASSWORD` | Contraseña de aplicación | `abcdefghijklmnop` |
| `SMTP_FROM_EMAIL` | Email remitente | `tucorreo@gmail.com` |
| `SMTP_FROM_NAME` | Nombre que aparece | `MAPO Sistema` |

---

## 🎯 Ejemplo con Diferentes Proveedores

### Gmail (Recomendado)
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tucorreo@gmail.com
SMTP_PASSWORD=tu-app-password-de-16-caracteres
SMTP_FROM_EMAIL=tucorreo@gmail.com
SMTP_FROM_NAME=MAPO Sistema
```

### Outlook / Hotmail
```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=tucorreo@outlook.com
SMTP_PASSWORD=tu-contraseña-normal
SMTP_FROM_EMAIL=tucorreo@outlook.com
SMTP_FROM_NAME=MAPO Sistema
```

### Yahoo Mail
```bash
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=tucorreo@yahoo.com
SMTP_PASSWORD=tu-app-password
SMTP_FROM_EMAIL=tucorreo@yahoo.com
SMTP_FROM_NAME=MAPO Sistema
```

---

## ⚠️ Problemas Comunes

### 1. Error: "Application-specific password required"
**Solución**: No estás usando la contraseña de aplicación. Genera una en https://myaccount.google.com/apppasswords

### 2. Error: "Username and Password not accepted"
**Solución**: 
- Verifica que la verificación en 2 pasos esté activada
- Asegúrate de copiar bien la contraseña de aplicación
- No incluyas espacios en la contraseña

### 3. Error: "Connection timeout"
**Solución**:
- Verifica tu conexión a internet
- Asegúrate de que el puerto 587 no esté bloqueado por firewall

### 4. No recibo emails
**Solución**:
- Revisa la carpeta de SPAM
- Verifica que el email destinatario sea correcto
- Revisa los logs de la consola para errores

---

## 🔒 Seguridad

### ✅ Buenas Prácticas:

1. **Nunca** compartas tu contraseña de aplicación
2. **Nunca** subas el archivo `.env` a Git (ya está en `.gitignore`)
3. Usa una cuenta de Gmail dedicada para el sistema (no tu personal)
4. Revoca contraseñas de aplicación que no uses
5. En producción, usa variables de entorno del servidor (no archivo .env)

### ❌ Malas Prácticas:

1. ❌ Usar tu contraseña normal de Gmail
2. ❌ Compartir credenciales en Slack/WhatsApp
3. ❌ Subir el .env a GitHub
4. ❌ Usar la misma contraseña para múltiples servicios

---

## 🚀 Configuración en Producción (DigitalOcean / Servidor)

En producción, las variables se configuran en el panel del servidor, **NO en el archivo .env**.

### DigitalOcean App Platform:
1. Ve a tu aplicación
2. Settings → App-Level Environment Variables
3. Agrega cada variable:
   - `SMTP_SERVER` = `smtp.gmail.com`
   - `SMTP_PORT` = `587`
   - `SMTP_USERNAME` = `tucorreo@gmail.com`
   - etc.

---

## 📞 ¿Necesitas Ayuda?

Si tienes problemas:
1. Revisa los logs de la consola
2. Verifica que las variables estén bien escritas (sin espacios extra)
3. Prueba primero sin configurar SMTP (modo desarrollo)
4. Asegúrate de que tu correo no requiera captcha o confirmación

---

## ✅ Checklist de Configuración

- [ ] Tengo una cuenta de Gmail
- [ ] Activé la verificación en 2 pasos
- [ ] Generé una contraseña de aplicación
- [ ] Copié la contraseña (sin espacios)
- [ ] Edité el archivo `.env`
- [ ] Reemplacé `SMTP_USERNAME` con mi correo
- [ ] Reemplacé `SMTP_PASSWORD` con la contraseña de app
- [ ] Reemplacé `SMTP_FROM_EMAIL` con mi correo
- [ ] Guardé el archivo
- [ ] Reinicié el servidor
- [ ] Probé el endpoint de reset
- [ ] ✅ ¡Funciona!
