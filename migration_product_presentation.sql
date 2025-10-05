-- Script para agregar columnas faltantes a product_presentation
-- Ejecutar este SQL en la base de datos PostgreSQL

-- Verificar si la columna price existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'product_presentation' 
        AND column_name = 'price'
    ) THEN
        ALTER TABLE product_presentation ADD COLUMN price FLOAT NOT NULL DEFAULT 0.0;
        RAISE NOTICE 'Columna price agregada a product_presentation';
    ELSE
        RAISE NOTICE 'Columna price ya existe en product_presentation';
    END IF;
END $$;

-- Verificar si la columna sku existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'product_presentation' 
        AND column_name = 'sku'
    ) THEN
        ALTER TABLE product_presentation ADD COLUMN sku VARCHAR;
        RAISE NOTICE 'Columna sku agregada a product_presentation';
    ELSE
        RAISE NOTICE 'Columna sku ya existe en product_presentation';
    END IF;
END $$;

-- Verificar si la columna active existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'product_presentation' 
        AND column_name = 'active'
    ) THEN
        ALTER TABLE product_presentation ADD COLUMN active INTEGER NOT NULL DEFAULT 1;
        RAISE NOTICE 'Columna active agregada a product_presentation';
    ELSE
        RAISE NOTICE 'Columna active ya existe en product_presentation';
    END IF;
END $$;

-- Mostrar estructura final de la tabla
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'product_presentation'
ORDER BY ordinal_position;