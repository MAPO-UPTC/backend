#!/bin/bash

# ====================================
# MAPO Backend - Droplet Setup Script
# ====================================
# Script para configurar inicial del droplet de DigitalOcean
# Ejecutar una sola vez después de crear el droplet

set -e  # Salir si hay errores

echo "🚀 Configurando droplet para MAPO Backend..."

# Actualizar sistema
echo "📦 Actualizando sistema..."
apt update && apt upgrade -y

# Instalar dependencias básicas
echo "🔧 Instalando dependencias básicas..."
apt install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# Instalar Docker
echo "🐳 Instalando Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl start docker
    systemctl enable docker
    usermod -aG docker root
    echo "✅ Docker instalado correctamente"
else
    echo "✅ Docker ya está instalado"
fi

# Instalar Docker Compose
echo "🐳 Instalando Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose instalado correctamente"
else
    echo "✅ Docker Compose ya está instalado"
fi

# Instalar PostgreSQL
echo "🐘 Instalando PostgreSQL..."
apt install -y postgresql postgresql-contrib
systemctl start postgresql
systemctl enable postgresql

# Configurar usuario y base de datos
echo "🔧 Configurando PostgreSQL..."
sudo -u postgres psql -c "CREATE USER mapo WITH PASSWORD 'a123';"
sudo -u postgres psql -c "CREATE DATABASE mapo_prod OWNER mapo;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mapo_prod TO mapo;"

# Configurar PostgreSQL para aceptar conexiones
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/g" /etc/postgresql/*/main/postgresql.conf
echo "host    all             all             127.0.0.1/32            md5" >> /etc/postgresql/*/main/pg_hba.conf
systemctl restart postgresql

echo "✅ PostgreSQL configurado correctamente"

# Configurar firewall básico
echo "🔒 Configurando firewall..."
ufw --force enable
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
echo "✅ Firewall configurado"

# Crear directorio para la aplicación
echo "📁 Creando directorios..."
mkdir -p /opt/mapo-backend
mkdir -p /opt/mapo-backend/logs
chown -R root:root /opt/mapo-backend

# Instalar Nginx (para proxy reverso)
echo "🌐 Instalando Nginx..."
apt install -y nginx
systemctl start nginx
systemctl enable nginx

# Configurar Nginx como proxy reverso
cat > /etc/nginx/sites-available/mapo-backend << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Habilitar sitio
ln -sf /etc/nginx/sites-available/mapo-backend /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# Configurar logrotate para logs de la aplicación
cat > /etc/logrotate.d/mapo-backend << 'EOF'
/opt/mapo-backend/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose -f /opt/mapo-backend/docker-compose.yml restart mapo-backend || true
    endscript
}
EOF

# Crear servicio systemd para auto-inicio
cat > /etc/systemd/system/mapo-backend.service << 'EOF'
[Unit]
Description=MAPO Backend Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/mapo-backend
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable mapo-backend

echo "✅ Configuración inicial completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Configura los secrets en GitHub Actions:"
echo "   - DROPLET_HOST: $(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)"
echo "   - DROPLET_USER: root"
echo "   - DROPLET_SSH_KEY: Tu clave privada SSH"
echo "   - DIGITALOCEAN_ACCESS_TOKEN: Tu token de DigitalOcean"
echo "   - DATABASE_URL: Tu URL de base de datos"
echo "   - FIREBASE_PRIVATE_KEY: Tu clave privada de Firebase"
echo "   - FIREBASE_PROJECT_ID: Tu ID de proyecto Firebase"
echo ""
echo "2. Ejecuta tu pipeline de GitHub Actions para deployar"
echo ""
echo "🎉 ¡Tu droplet está listo para recibir deployments!"