# 🚀 MAPO Backend - Deployment con DigitalOcean Droplet

Esta guía te ayudará a configurar el deployment automático de MAPO Backend en un droplet de DigitalOcean usando GitHub Actions.

## 📋 Prerrequisitos

- ✅ Droplet de DigitalOcean creado con SSH
- ✅ Cuenta de DigitalOcean con Container Registry habilitado
- ✅ Repositorio en GitHub con Actions habilitadas

## 🛠️ Configuración Inicial del Droplet

### 1. Conectar al Droplet via SSH
```bash
ssh root@YOUR_DROPLET_IP
```

### 2. Ejecutar Script de Configuración
```bash
# Descargar y ejecutar el script de setup
curl -fsSL https://raw.githubusercontent.com/MAPO-UPTC/backend/main/deployment/setup-droplet.sh -o setup-droplet.sh
chmod +x setup-droplet.sh
./setup-droplet.sh
```

## 🔑 Configuración de GitHub Secrets

Ve a tu repositorio en GitHub: `Settings` → `Secrets and variables` → `Actions`

### Secrets Requeridos:

| Secret Name | Descripción | Cómo Obtenerlo |
|-------------|-------------|----------------|
| `DIGITALOCEAN_ACCESS_TOKEN` | Token de API de DigitalOcean | [DigitalOcean API Tokens](https://cloud.digitalocean.com/account/api/tokens) |
| `DROPLET_HOST` | IP pública del droplet | `ip addr show` en el droplet |
| `DROPLET_USER` | Usuario SSH | `root` (por defecto) |
| `DROPLET_SSH_KEY` | Clave privada SSH | Tu clave privada (~/.ssh/id_rsa) |
| `DATABASE_URL` | URL de la base de datos | `postgresql://user:pass@host:port/dbname` |
| `FIREBASE_PRIVATE_KEY` | Clave privada Firebase | Firebase Console → Project Settings → Service accounts |
| `FIREBASE_PROJECT_ID` | ID del proyecto Firebase | Firebase Console → Project Settings |

### Ejemplo de valores:
```bash
DIGITALOCEAN_ACCESS_TOKEN=dop_v1_abcdef123456789...
DROPLET_HOST=164.90.123.456
DROPLET_USER=root
DROPLET_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHIAAAAGYmNyeXB0AAAAGAAAABQ...
DATABASE_URL=postgresql://mapo_user:secure_password@localhost:5432/mapo_db
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...
FIREBASE_PROJECT_ID=mapo-backend-prod
```

## 🚀 Proceso de Deployment

### Workflow Automático
El deployment se ejecuta automáticamente cuando:
- ✅ Push a la rama `main`
- ✅ Pull Request merge a `main`

### Pasos del Pipeline:
1. **🧪 Testing**: Ejecuta todos los tests
2. **🔍 Code Quality**: Verifica Black, isort, flake8
3. **🛡️ Security**: Escaneo con Bandit
4. **🐳 Docker Build**: Construye y sube imagen al registry
5. **🚀 Deploy**: Despliega al droplet via SSH

### Deployment Manual
```bash
# Forzar deployment desde Actions tab
gh workflow run deploy.yml --ref main
```

## 🐳 Configuración Docker

El deployment usa Docker Compose con la siguiente configuración:

```yaml
version: '3.8'
services:
  mapo-backend:
    image: registry.digitalocean.com/mapo-backend:latest
    ports:
      - "80:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - FIREBASE_PRIVATE_KEY=${FIREBASE_PRIVATE_KEY}
      - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
      - ENVIRONMENT=production
      - DEBUG=false
    restart: unless-stopped
```

## 🌐 Configuración Nginx

Nginx actúa como proxy reverso:
- ✅ Puerto 80 → Aplicación FastAPI (puerto 8000)
- ✅ Headers de proxy configurados
- ✅ Health check endpoint habilitado

## 📊 Monitoreo y Logs

### Ver logs de la aplicación:
```bash
# Logs del contenedor
docker-compose -f /opt/mapo-backend/docker-compose.yml logs -f

# Logs de Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Health Check:
```bash
curl http://YOUR_DROPLET_IP/health
```

### Estado de servicios:
```bash
# Estado de contenedores Docker
docker-compose -f /opt/mapo-backend/docker-compose.yml ps

# Estado de servicios del sistema
systemctl status nginx
systemctl status docker
systemctl status mapo-backend
```

## 🔧 Comandos Útiles

### En el Droplet:
```bash
# Reiniciar aplicación
cd /opt/mapo-backend
docker-compose restart

# Actualizar manualmente
docker-compose pull
docker-compose up -d

# Ver recursos del sistema
htop
df -h
free -m
```

### Desde tu máquina local:
```bash
# SSH al droplet
ssh root@YOUR_DROPLET_IP

# Copiar archivos al droplet
scp file.txt root@YOUR_DROPLET_IP:/opt/mapo-backend/

# Ejecutar comandos remotos
ssh root@YOUR_DROPLET_IP "docker-compose -f /opt/mapo-backend/docker-compose.yml ps"
```

## 🔍 Troubleshooting

### Problema: Deployment falla en SSH
```bash
# Verificar conectividad SSH
ssh root@YOUR_DROPLET_IP echo "SSH OK"

# Verificar clave SSH en GitHub Secrets
cat ~/.ssh/id_rsa  # Copia completa incluyendo headers
```

### Problema: Docker no se puede conectar al registry
```bash
# Login manual al registry
echo $DIGITALOCEAN_ACCESS_TOKEN | docker login registry.digitalocean.com -u $DIGITALOCEAN_ACCESS_TOKEN --password-stdin
```

### Problema: Aplicación no responde
```bash
# Verificar logs
docker-compose -f /opt/mapo-backend/docker-compose.yml logs

# Verificar puertos
netstat -tlnp | grep :80
netstat -tlnp | grep :8000

# Reiniciar servicios
systemctl restart nginx
docker-compose -f /opt/mapo-backend/docker-compose.yml restart
```

## 🎯 Próximos Pasos

1. ✅ Configurar HTTPS con Let's Encrypt
2. ✅ Implementar backup automático de DB
3. ✅ Configurar monitoring con Prometheus/Grafana
4. ✅ Implementar auto-scaling

---

¿Necesitas ayuda? Revisa los logs del GitHub Actions workflow o los logs del droplet para más detalles.