# ====================================
# GUÍA DE DESPLIEGUE EN DIGITALOCEAN
# ====================================

## 📋 PREREQUISITOS

1. **Cuenta de DigitalOcean** con acceso a:
   - App Platform (para el backend)
   - Managed Databases (PostgreSQL)
   - Spaces (opcional, para archivos estáticos)

2. **Credenciales de Firebase** configuradas
3. **Dominio** configurado (opcional pero recomendado)

## 🚀 OPCIÓN 1: DigitalOcean App Platform (Recomendado)

### Paso 1: Preparar el repositorio
```bash
# Asegúrate de que todos los archivos estén committeados
git add .
git commit -m "Preparar para despliegue"
git push origin main
```

### Paso 2: Crear base de datos
1. Ve a **DigitalOcean Dashboard > Databases**
2. **Create Database** > PostgreSQL
3. Configuración recomendada:
   - **Engine**: PostgreSQL 15
   - **Plan**: Basic ($15/mes para comenzar)
   - **Datacenter**: Mismo que tu app
4. **Guardar** la connection string que se genera

### Paso 3: Crear App en App Platform
1. Ve a **DigitalOcean Dashboard > Apps**
2. **Create App** > **GitHub** (conecta tu repositorio)
3. Configuración:
   - **Source**: Tu repositorio GitHub
   - **Branch**: main
   - **Autodeploy**: Habilitado

### Paso 4: Configurar la app
```yaml
# App Platform detectará automáticamente el Dockerfile
# Configuración sugerida:
name: mapo-backend
services:
- name: api
  source_dir: /
  github:
    repo: tu-usuario/tu-repo
    branch: main
  run_command: uvicorn main:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /
```

### Paso 5: Variables de entorno
En **App Platform > Settings > Environment Variables**, añadir:

```bash
# Base de datos (usar la connection string de DigitalOcean)
DATABASE_URL=postgresql://username:password@host:25060/database?sslmode=require

# Firebase (copiar desde .env)
FIREBASE_PROJECT_ID=tu-project-id
FIREBASE_PRIVATE_KEY=tu-private-key
FIREBASE_CLIENT_EMAIL=tu-client-email
FIREBASE_API_KEY=tu-api-key
# ... (todas las variables de Firebase)

# Aplicación
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=tu-secret-key-super-seguro

# CORS (reemplazar con tu dominio real)
ALLOWED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com

# Logging
LOG_LEVEL=info
```

## 🐳 OPCIÓN 2: DigitalOcean Droplet con Docker

### Paso 1: Crear Droplet
1. **Create Droplet** en DigitalOcean
2. **Ubuntu 22.04 LTS**
3. **Regular Intel** - $6/mes para comenzar
4. Agregar tu **SSH Key**

### Paso 2: Conectar y configurar servidor
```bash
# Conectar al droplet
ssh root@tu-ip-droplet

# Actualizar sistema
apt update && apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Paso 3: Clonar y configurar proyecto
```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/tu-repo.git
cd tu-repo

# Copiar y configurar variables de entorno
cp .env.example .env
nano .env  # Editar con tus valores reales

# Construir e iniciar
docker-compose up -d --build
```

### Paso 4: Configurar Nginx (Proxy reverso)
```bash
# Instalar Nginx
apt install nginx -y

# Configurar virtual host
nano /etc/nginx/sites-available/mapo-backend
```

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Habilitar sitio
ln -s /etc/nginx/sites-available/mapo-backend /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Configurar SSL con Let's Encrypt
apt install certbot python3-certbot-nginx -y
certbot --nginx -d tu-dominio.com
```

## 🔧 CONFIGURACIÓN POST-DESPLIEGUE

### Verificar deployment
```bash
# Verificar salud de la app
curl https://tu-dominio.com/health

# Verificar logs
# En App Platform: ve a Runtime Logs
# En Droplet: docker-compose logs -f
```

### Configurar base de datos
```bash
# Ejecutar migraciones si es necesario
# En App Platform: usar Console
# En Droplet: docker-compose exec app python manage.py migrate
```

### Configurar monitoreo
1. **DigitalOcean Monitoring**: Habilitado automáticamente
2. **Uptime checks**: Configurar en `/health` endpoint
3. **Alertas**: Email cuando la app esté down

## 📊 COSTOS ESTIMADOS MENSUALES

### App Platform (Opción 1)
- **App**: $5/mes (Basic)
- **Database**: $15/mes (Basic PostgreSQL)
- **Total**: ~$20/mes

### Droplet + Database (Opción 2)
- **Droplet**: $6/mes (1GB RAM)
- **Database**: $15/mes (Managed PostgreSQL)
- **Total**: ~$21/mes

## 🔒 CHECKLIST DE SEGURIDAD

- [ ] Variables de entorno configuradas (no hardcodeadas)
- [ ] SSL/HTTPS habilitado
- [ ] Firewall configurado (solo puertos 80, 443, 22)
- [ ] Database con SSL requerido
- [ ] CORS configurado solo para dominios permitidos
- [ ] Logging habilitado para auditoría
- [ ] Backups automáticos de base de datos

## 🆘 SOLUCIÓN DE PROBLEMAS

### App no inicia
1. Verificar logs en DigitalOcean Dashboard
2. Verificar variables de entorno
3. Probar health check: `/health`

### Error de base de datos
1. Verificar connection string
2. Verificar que SSL esté habilitado
3. Verificar firewall de database

### Error de Firebase
1. Verificar que todas las variables de Firebase estén configuradas
2. Verificar formato de FIREBASE_PRIVATE_KEY (saltos de línea)
3. Verificar permisos en Firebase Console

## 📞 SOPORTE

- **DigitalOcean**: https://docs.digitalocean.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Firebase**: https://firebase.google.com/docs