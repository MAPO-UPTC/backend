# 🚀 CI/CD Pipeline - MAPO Backend

Documentación completa del pipeline de CI/CD automatizado para el backend MAPO usando GitHub Actions y DigitalOcean.

## 📋 Workflows Configurados

### 1. 🧪 **Testing Workflow** (`test.yml`)
- **Trigger**: Pull Requests, pushes a ramas feature/bugfix/hotfix
- **Propósito**: Validación rápida de código
- **Jobs**:
  - ⚡ Quick Tests: Tests unitarios básicos
  - 🔍 Code Quality: Linting y formatting
  - 🔒 Security Check: Verificación de secretos hardcodeados

### 2. 🚀 **Deploy Workflow** (`deploy.yml`)
- **Trigger**: Push a `main` (producción) o `develop` (staging)
- **Propósito**: Despliegue completo con testing
- **Jobs**:
  - 🧪 Testing & Linting completo
  - 🔒 Security Scan avanzado
  - 🐳 Docker Build & Push
  - 🚀 Deploy a DigitalOcean
  - 📢 Notificaciones

## 🔧 Configuración Requerida

### GitHub Secrets
Configurar en: `Repository Settings > Secrets and Variables > Actions`

```bash
# DigitalOcean
DIGITALOCEAN_ACCESS_TOKEN=tu_token_aqui
DIGITALOCEAN_APP_ID=tu_app_id_aqui

# Base de Datos
DATABASE_URL=postgresql://user:password@host:port/database

# Firebase
FIREBASE_PROJECT_ID=tu_project_id
FIREBASE_PRIVATE_KEY=tu_private_key
FIREBASE_CLIENT_EMAIL=tu_client_email
FIREBASE_API_KEY=tu_api_key
FIREBASE_AUTH_DOMAIN=tu_auth_domain
FIREBASE_STORAGE_BUCKET=tu_storage_bucket
FIREBASE_MESSAGING_SENDER_ID=tu_sender_id
FIREBASE_APP_ID=tu_app_id

# Aplicación
SECRET_KEY=tu_secret_key_super_segura
```

### DigitalOcean Container Registry
1. Crear Container Registry en DigitalOcean
2. Configurar nombre: `mapo-backend`
3. El workflow automáticamente hace push de imágenes

## 🌊 Flujo de Trabajo

### Desarrollo Normal
```bash
# 1. Crear feature branch
git checkout -b feature/nueva-funcionalidad

# 2. Desarrollar y commit
git add .
git commit -m "feat: nueva funcionalidad"

# 3. Push y crear PR
git push origin feature/nueva-funcionalidad
# → Trigger: test.yml (testing rápido)

# 4. Merge a develop
# → Trigger: deploy.yml (deploy a staging)

# 5. Merge a main
# → Trigger: deploy.yml (deploy a producción)
```

### Hotfixes
```bash
# 1. Crear hotfix desde main
git checkout main
git checkout -b hotfix/fix-critico

# 2. Fix y push
git commit -m "fix: problema crítico"
git push origin hotfix/fix-critico
# → Trigger: test.yml

# 3. Merge directo a main
# → Trigger: deploy.yml (producción)
```

## 🐳 Docker Registry

### Imágenes Generadas
- `registry.digitalocean.com/mapo-backend:latest` - Última versión de main
- `registry.digitalocean.com/mapo-backend:develop` - Última versión de develop
- `registry.digitalocean.com/mapo-backend:main-sha123456` - Version específica

### Tags Automáticos
- `latest`: Último push a main
- `develop`: Último push a develop
- `{branch}-{sha}`: Tags únicos por commit

## 📊 Monitoreo y Logs

### Health Checks
- **URL**: `/health`
- **Intervalo**: Cada 10 segundos
- **Timeout**: 5 segundos
- **Reintentos**: 3 fallos antes de restart

### Logs Automáticos
- Build logs en GitHub Actions
- Application logs en DigitalOcean App Platform
- Database logs en DigitalOcean Managed Database

## 🔄 Rollback

### Rollback Automático
```bash
# Revertir último deploy
doctl apps update $APP_ID --spec deployment/app-spec.yaml

# O usar imagen anterior específica
# Editar app-spec.yaml con tag anterior y re-deploy
```

### Rollback Manual
1. Ir a DigitalOcean App Platform Dashboard
2. Seleccionar deployment anterior
3. Click "Redeploy"

## 🚨 Troubleshooting

### Deploy Falla
1. Revisar logs en GitHub Actions
2. Verificar secrets configurados
3. Comprobar Docker build
4. Validar app-spec.yaml

### Tests Fallan
1. Revisar output de pytest
2. Verificar imports (PYTHONPATH)
3. Comprobar variables de entorno
4. Validar estructura de archivos

### Database Issues
1. Verificar DATABASE_URL
2. Comprobar migrations
3. Revisar permisos de usuario
4. Validar conexión de red

## 🎯 Mejoras Futuras

- [ ] Tests de integración más completos
- [ ] Métricas de performance
- [ ] Alerts automáticos
- [ ] Blue-green deployments
- [ ] Automatic database migrations
- [ ] Slack/Discord notifications

---

**📌 Nota**: Este pipeline está configurado para máxima automatización y seguridad. Cualquier push activa validaciones automáticas.