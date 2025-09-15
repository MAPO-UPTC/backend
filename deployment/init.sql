-- ====================================
-- SCRIPT DE INICIALIZACIÓN DE BASE DE DATOS
-- ====================================

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear esquemas si no existen
CREATE SCHEMA IF NOT EXISTS public;

-- Configuraciones de base de datos
SET timezone = 'UTC';

-- Crear función para actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Comentarios informativos
COMMENT ON DATABASE mapo IS 'Base de datos principal para MAPO Backend API';

-- Log de inicialización
DO $$
BEGIN
    RAISE NOTICE '✅ Base de datos inicializada correctamente';
    RAISE NOTICE '📅 Timestamp: %', CURRENT_TIMESTAMP;
    RAISE NOTICE '🆔 Database: %', CURRENT_DATABASE();
END $$;