# 📦➡️🌾 Guía: Convertir Producto Empaquetado a Granel

## 📌 Descripción General

Esta guía explica cómo implementar en el **frontend** la funcionalidad para **convertir productos empaquetados a granel**. Esta operación permite "abrir un bulto" de productos empaquetados y habilitarlo para venta a granel (por unidad suelta).

---

## 🎯 ¿Qué es una Conversión a Granel?

### Ejemplo Práctico:

Tienes **10 paquetes de arroz de 500g** en tu inventario empaquetado.

**Operación**: Abres 1 paquete → Ahora tienes:
- ✅ **9 paquetes cerrados** (stock empaquetado)
- ✅ **500g de arroz suelto** disponible para venta a granel

**Resultado**: Los clientes pueden comprar arroz en cantidades menores (ej: 100g, 250g) del paquete abierto.

---

## 🔗 Endpoint

### **POST** `/products/open-bulk/`

Abre un bulto/paquete y lo convierte a stock a granel.

---

## 🔐 Autenticación

**Requiere autenticación con Bearer Token:**

```typescript
headers: {
  'Authorization': `Bearer ${token}`
}
```

**Requiere permisos**: `PRODUCTS:UPDATE` (Solo usuarios con permisos de actualizar productos)

---

## 📥 Request Body

### Estructura del Request

```typescript
interface BulkConversionCreate {
  source_lot_detail_id: string;      // UUID del lote empaquetado
  target_presentation_id: string;    // UUID de la presentación "granel"
  converted_quantity: number;        // Cantidad de bultos/paquetes a abrir (entero)
  unit_conversion_factor: number;    // Cantidad que contiene cada bulto (entero)
}
```

### Ejemplo de Request

```json
{
  "source_lot_detail_id": "550e8400-e29b-41d4-a716-446655440000",
  "target_presentation_id": "660e8400-e29b-41d4-a716-446655440001",
  "converted_quantity": 1,
  "unit_conversion_factor": 500
}
```

### Explicación de los Campos

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `source_lot_detail_id` | UUID (string) | ID del lote empaquetado que se va a abrir | UUID del "Paquete x 500g" |
| `target_presentation_id` | UUID (string) | ID de la presentación "granel" donde se guardará | UUID de "Granel (gramos)" |
| `converted_quantity` | number (int) | **Cantidad de bultos/paquetes a abrir** | 1 (abrir 1 paquete) |
| `unit_conversion_factor` | number (int) | **Cantidad que contiene cada bulto** | 500 (cada paquete tiene 500g) |

### 📊 Cálculo de Conversión

**Fórmula**:
```
Total a granel = converted_quantity × unit_conversion_factor
```

**Ejemplos**:
- Abrir **1 paquete** de **500g** = `1 × 500 = 500g` a granel
- Abrir **2 paquetes** de **500g** = `2 × 500 = 1000g` a granel
- Abrir **1 caja** de **100 tabletas** = `1 × 100 = 100 tabletas` a granel
- Abrir **1 bulto** de **25kg** = `1 × 25000 = 25000g` a granel

---

## 📤 Respuesta

### Estructura de la Respuesta

```typescript
interface BulkConversionResponse {
  message: string;
  bulk_conversion_id: string;        // UUID de la conversión creada
  converted_quantity: number;        // Cantidad de bultos convertidos
  remaining_bulk: number;            // Cantidad disponible a granel
  total_bulk_created: number;        // Total creado a granel
  unit_conversion_factor: number;    // Factor de conversión usado
  status: string;                    // Estado: "ACTIVE", "COMPLETED", "CANCELLED"
}
```

### Ejemplo de Respuesta Exitosa

```json
{
  "message": "Bulto(s) abierto(s) exitosamente. 500 unidades disponibles a granel",
  "bulk_conversion_id": "770e8400-e29b-41d4-a716-446655440002",
  "converted_quantity": 1,
  "remaining_bulk": 500,
  "total_bulk_created": 500,
  "unit_conversion_factor": 500,
  "status": "ACTIVE"
}
```

---

## 🚀 Implementación en Frontend

### 1. **Servicio API** (TypeScript)

```typescript
// services/bulkConversionService.ts
import axios from 'axios';

const API_URL = 'http://localhost:8000';

interface BulkConversionCreate {
  source_lot_detail_id: string;
  target_presentation_id: string;
  converted_quantity: number;        // Cantidad de bultos a abrir
  unit_conversion_factor: number;    // Cantidad que contiene cada bulto
}

interface BulkConversionResponse {
  message: string;
  bulk_conversion_id: string;
  converted_quantity: number;
  remaining_bulk: number;
  total_bulk_created: number;
  unit_conversion_factor: number;
  status: string;
}

/**
 * Abrir bulto(s)/paquete(s) y convertirlo a granel
 * 
 * @param data - Datos de la conversión
 * @param token - Token de autenticación
 * 
 * @example
 * // Abrir 1 paquete de 500g
 * await openBulkConversion({
 *   source_lot_detail_id: "uuid-del-lote",
 *   target_presentation_id: "uuid-granel",
 *   converted_quantity: 1,        // Abrir 1 paquete
 *   unit_conversion_factor: 500   // Contiene 500g
 * }, token);
 * // Resultado: 500g disponibles a granel
 * 
 * @example
 * // Abrir 2 bultos de 25kg
 * await openBulkConversion({
 *   source_lot_detail_id: "uuid-del-lote",
 *   target_presentation_id: "uuid-granel",
 *   converted_quantity: 2,        // Abrir 2 bultos
 *   unit_conversion_factor: 25000 // Cada bulto tiene 25kg = 25000g
 * }, token);
 * // Resultado: 50000g (50kg) disponibles a granel
 */
export const openBulkConversion = async (
  data: BulkConversionCreate,
  token: string
): Promise<BulkConversionResponse> => {
  try {
    // Validar datos antes de enviar
    if (data.converted_quantity <= 0) {
      throw new Error('La cantidad de bultos debe ser mayor a 0');
    }
    if (data.unit_conversion_factor <= 0) {
      throw new Error('El factor de conversión debe ser mayor a 0');
    }
    
    const response = await axios.post(
      `${API_URL}/products/open-bulk/`,
      data,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 404) {
        throw new Error('Lote no encontrado');
      }
      if (error.response?.status === 400) {
        const detail = error.response?.data?.detail;
        if (detail?.includes('suficientes bultos')) {
          throw new Error(detail); // Mensaje específico de bultos insuficientes
        }
        throw new Error(detail || 'No hay bultos disponibles');
      }
      if (error.response?.status === 403) {
        throw new Error('No tienes permisos para realizar esta operación');
      }
      throw new Error(error.response?.data?.detail || 'Error al abrir bulto');
    }
    throw error;
  }
};

/**
 * Obtener stock a granel activo
 */
export const getActiveBulkStock = async (
  token: string
): Promise<BulkStockItem[]> => {
  try {
    const response = await axios.get(
      `${API_URL}/products/bulk-stock/`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'Error al obtener stock a granel');
    }
    throw error;
  }
};

interface BulkStockItem {
  bulk_conversion_id: string;
  remaining_bulk: number;
  converted_quantity: number;
  target_presentation_id: string;
  conversion_date: string;
  status: string;
}
```

---

### 2. **Hook Personalizado** (React)

```typescript
// hooks/useBulkConversion.ts
import { useState } from 'react';
import { openBulkConversion, BulkConversionCreate, BulkConversionResponse } from '../services/bulkConversionService';

interface UseBulkConversionResult {
  convertToBulk: (data: BulkConversionCreate) => Promise<BulkConversionResponse>;
  loading: boolean;
  error: string | null;
  success: boolean;
  resetState: () => void;
}

/**
 * Hook para manejar conversión a granel
 * 
 * @example
 * const { convertToBulk, loading, error } = useBulkConversion(token);
 * 
 * // Abrir 1 paquete de 500g
 * await convertToBulk({
 *   source_lot_detail_id: lotId,
 *   target_presentation_id: granelId,
 *   converted_quantity: 1,
 *   unit_conversion_factor: 500
 * });
 */
export const useBulkConversion = (token: string): UseBulkConversionResult => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const convertToBulk = async (data: BulkConversionCreate): Promise<BulkConversionResponse> => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await openBulkConversion(data, token);
      setSuccess(true);
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const resetState = () => {
    setError(null);
    setSuccess(false);
  };

  return {
    convertToBulk,
    loading,
    error,
    success,
    resetState
  };
};
```

---

### 3. **Componente: Modal de Conversión** (React)

```typescript
// components/BulkConversionModal.tsx
import React, { useState, useEffect } from 'react';
import { useBulkConversion } from '../hooks/useBulkConversion';

interface BulkConversionModalProps {
  lotDetailId: string;              // ID del lote empaquetado
  productName: string;              // Nombre del producto
  presentationName: string;         // Nombre de la presentación empaquetada
  unitConversionFactor: number;     // Cantidad que contiene cada bulto
  availablePackages: number;        // Cantidad de paquetes disponibles
  onClose: () => void;
  onSuccess: () => void;
}

/**
 * Modal para abrir bulto(s) y convertir a granel
 * 
 * @example
 * <BulkConversionModal
 *   lotDetailId="uuid-123"
 *   productName="Arroz Integral"
 *   presentationName="Bulto x 25kg"
 *   unitConversionFactor={25000}  // 25kg = 25000g
 *   availablePackages={10}
 *   onClose={() => setShowModal(false)}
 *   onSuccess={() => refetchInventory()}
 * />
 */
export const BulkConversionModal: React.FC<BulkConversionModalProps> = ({
  lotDetailId,
  productName,
  presentationName,
  unitConversionFactor,
  availablePackages,
  onClose,
  onSuccess
}) => {
  const token = localStorage.getItem('authToken') || '';
  const { convertToBulk, loading, error, success } = useBulkConversion(token);

  const [targetPresentationId, setTargetPresentationId] = useState('');
  const [convertedQuantity, setConvertedQuantity] = useState<number>(1); // Cantidad de bultos a abrir
  const [presentations, setPresentations] = useState<any[]>([]);

  // Calcular total a granel
  const totalBulkToCreate = convertedQuantity * unitConversionFactor;

  // Cargar presentaciones "granel" disponibles
  useEffect(() => {
    // Aquí deberías cargar las presentaciones de tipo "granel"
    // desde tu API de productos
    fetchGranelPresentations();
  }, []);

  const fetchGranelPresentations = async () => {
    // Implementar llamada a API para obtener presentaciones tipo "granel"
    // Por ejemplo: GET /products/{product_id}/presentations?type=granel
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!targetPresentationId) {
      alert('Por favor selecciona una presentación granel');
      return;
    }

    if (convertedQuantity <= 0) {
      alert('La cantidad debe ser mayor a 0');
      return;
    }

    if (convertedQuantity > availablePackages) {
      alert(`Solo hay ${availablePackages} paquete(s) disponible(s)`);
      return;
    }

    try {
      const result = await convertToBulk({
        source_lot_detail_id: lotDetailId,
        target_presentation_id: targetPresentationId,
        converted_quantity: convertedQuantity,         // Bultos a abrir
        unit_conversion_factor: unitConversionFactor   // Cantidad por bulto
      });

      alert(
        `✅ ${result.message}\n\n` +
        `Bultos abiertos: ${result.converted_quantity}\n` +
        `Total disponible a granel: ${result.total_bulk_created} unidades\n` +
        `Factor de conversión: ${result.unit_conversion_factor}`
      );
      
      onSuccess();
      onClose();
    } catch (err) {
      console.error('Error al convertir a granel:', err);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>📦➡️🌾 Abrir Bulto(s) para Granel</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="product-info">
          <h3>{productName}</h3>
          <p><strong>Presentación:</strong> {presentationName}</p>
          <p><strong>Paquetes disponibles:</strong> {availablePackages}</p>
          <p><strong>Cantidad por paquete:</strong> {unitConversionFactor} unidades</p>
          
          <div className="info-box">
            <p className="info-text">
              ℹ️ Al abrir {convertedQuantity} bulto(s), se:
            </p>
            <ul>
              <li>Restarán {convertedQuantity} paquete(s) del inventario empaquetado</li>
              <li>Crearán {totalBulkToCreate.toLocaleString()} unidades a granel</li>
            </ul>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="convertedQuantity">
              ¿Cuántos bultos deseas abrir? *
            </label>
            <input
              type="number"
              id="convertedQuantity"
              value={convertedQuantity}
              onChange={(e) => setConvertedQuantity(parseInt(e.target.value) || 1)}
              min="1"
              max={availablePackages}
              required
            />
            <small className="help-text">
              Número de bultos/paquetes que deseas abrir (disponibles: {availablePackages})
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="targetPresentation">
              Presentación Granel *
            </label>
            <select
              id="targetPresentation"
              value={targetPresentationId}
              onChange={(e) => setTargetPresentationId(e.target.value)}
              required
            >
              <option value="">Seleccione presentación...</option>
              {presentations.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.presentation_name} ({p.unit})
                </option>
              ))}
            </select>
            <small className="help-text">
              Selecciona la presentación donde se guardará el stock a granel
            </small>
          </div>

          <div className="summary-box">
            <h4>📊 Resumen de Conversión</h4>
            <div className="summary-item">
              <span>Bultos a abrir:</span>
              <strong>{convertedQuantity}</strong>
            </div>
            <div className="summary-item">
              <span>Cantidad por bulto:</span>
              <strong>{unitConversionFactor.toLocaleString()} unidades</strong>
            </div>
            <div className="summary-item highlight">
              <span>Total a crear a granel:</span>
              <strong>{totalBulkToCreate.toLocaleString()} unidades</strong>
            </div>
          </div>

          {error && (
            <div className="alert alert-error">
              ❌ {error}
            </div>
          )}

          {success && (
            <div className="alert alert-success">
              ✅ Bulto(s) abierto(s) exitosamente
            </div>
          )}

          <div className="modal-footer">
            <button
              type="button"
              className="btn-cancel"
              onClick={onClose}
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={loading || availablePackages < 1 || !targetPresentationId}
            >
              {loading ? 'Abriendo...' : `Abrir ${convertedQuantity} Bulto(s)`}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
```

---

### 4. **CSS para el Modal**

```css
/* styles/BulkConversionModal.css */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 16px;
  margin-bottom: 20px;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 32px;
  height: 32px;
}

.close-btn:hover {
  color: #ef4444;
}

.product-info {
  background: #f9fafb;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.product-info h3 {
  margin: 0 0 12px 0;
  color: #111827;
  font-size: 18px;
}

.product-info p {
  margin: 8px 0;
  color: #374151;
}

.info-text {
  background: #dbeafe;
  padding: 12px;
  border-radius: 6px;
  color: #1e40af;
  font-size: 14px;
  margin-top: 12px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.help-text {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #6b7280;
}

.summary-box {
  background: #f0f9ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 16px;
}

.summary-box h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1e40af;
}

.summary-box p {
  margin: 4px 0;
  font-size: 13px;
  color: #1e3a8a;
}

.alert {
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 16px;
}

.alert-error {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.alert-success {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 2px solid #e5e7eb;
}

.btn-cancel,
.btn-primary {
  padding: 10px 20px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
}

.btn-cancel:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled,
.btn-cancel:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

---

## 📋 Flujo Completo de Uso

### 1. **Usuario ve el inventario empaquetado**
```
Producto: Arroz Diana - Paquete x 500g
Stock disponible: 10 paquetes
```

### 2. **Usuario hace clic en "Abrir para Granel"**
Se abre el modal `BulkConversionModal`

### 3. **Usuario completa el formulario**
- Selecciona presentación granel: "Granel (gramos)"
- Ingresa **cuántos bultos abrir**: 2
- Ingresa **cantidad por bulto**: 25000 (25kg)
- Ve el resumen: **Total a crear: 50000g (50kg)**

### 4. **Sistema procesa la conversión**
```typescript
POST /products/open-bulk/
{
  "source_lot_detail_id": "uuid-del-lote",
  "target_presentation_id": "uuid-presentacion-granel",
  "converted_quantity": 2,  // 2 bultos
  "unit_conversion_factor": 25000  // 25kg por bulto = 25000g
}
```

### 5. **Backend actualiza inventario**
- ✅ Resta **2** del stock empaquetado (ahora: 8 paquetes)
- ✅ Crea registro en `bulk_conversion` con **50000g** disponibles (2 × 25000)
- ✅ Estado: "ACTIVE"

### 6. **Usuario puede vender a granel**
Ahora puede vender cantidades menores:
- 100g de arroz
- 250g de arroz
- etc.

---

## 🔍 Consultar Stock a Granel Activo

### Endpoint: **GET** `/products/bulk-stock/`

```typescript
// Obtener todo el stock a granel activo
const activeBulk = await getActiveBulkStock(token);

// Respuesta
[
  {
    "bulk_conversion_id": "770e8400-e29b-41d4-a716-446655440002",
    "remaining_bulk": 350,
    "converted_quantity": 500,
    "target_presentation_id": "660e8400-e29b-41d4-a716-446655440001",
    "conversion_date": "2025-10-13T10:30:00",
    "status": "ACTIVE"
  }
]
```

**Significado:**
- Se abrió un bulto con 500 unidades
- Se han vendido 150 unidades (500 - 350)
- Quedan 350 unidades disponibles para venta a granel

---

## ⚠️ Validaciones Importantes

### 1. **Antes de Abrir Bulto**
```typescript
if (availablePackages < 1) {
  throw new Error('No hay paquetes disponibles para abrir');
}
```

### 2. **Cantidad Debe Ser Entera**
```typescript
quantity: number; // Debe ser entero (int)
```

### 3. **Presentación Granel Debe Existir**
Asegúrate de tener una presentación de tipo "granel" creada para el producto.

### 4. **Permisos Requeridos**
Usuario debe tener permiso `PRODUCTS:UPDATE`

---

## 📊 Ejemplo Completo de Integración

### En Componente de Inventario

```typescript
// components/InventoryTable.tsx
import React, { useState } from 'react';
import { BulkConversionModal } from './BulkConversionModal';

export const InventoryTable: React.FC = () => {
  const [selectedLot, setSelectedLot] = useState<any>(null);

  const handleOpenBulk = (lot: any) => {
    setSelectedLot(lot);
  };

  const handleCloseModal = () => {
    setSelectedLot(null);
  };

  const handleSuccess = () => {
    // Recargar inventario
    refreshInventory();
  };

  return (
    <>
      <table className="inventory-table">
        <thead>
          <tr>
            <th>Producto</th>
            <th>Presentación</th>
            <th>Stock</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {inventory.map((item) => (
            <tr key={item.id}>
              <td>{item.product_name}</td>
              <td>{item.presentation_name}</td>
              <td>{item.quantity_available} paquetes</td>
              <td>
                <button
                  onClick={() => handleOpenBulk(item)}
                  disabled={item.quantity_available < 1}
                  className="btn-open-bulk"
                >
                  📦➡️🌾 Abrir para Granel
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {selectedLot && (
        <BulkConversionModal
          lotDetailId={selectedLot.id}
          productName={selectedLot.product_name}
          presentationName={selectedLot.presentation_name}
          availablePackages={selectedLot.quantity_available}
          onClose={handleCloseModal}
          onSuccess={handleSuccess}
        />
      )}
    </>
  );
};
```

---

## ❌ Manejo de Errores

### Códigos de Error HTTP

| Código | Error | Solución |
|--------|-------|----------|
| **400** | No hay bultos disponibles | Verificar que `quantity_available >= 1` |
| **403** | Sin permisos | Usuario debe tener rol con `PRODUCTS:UPDATE` |
| **404** | Lote no encontrado | Verificar que el `source_lot_detail_id` sea correcto |
| **500** | Error interno | Revisar logs del servidor |

### Ejemplo de Manejo

```typescript
try {
  await convertToBulk(data);
} catch (error) {
  if (error.message.includes('No hay bultos disponibles')) {
    alert('⚠️ No tienes paquetes disponibles para abrir');
  } else if (error.message.includes('Sin permisos')) {
    alert('⚠️ No tienes permisos para realizar esta operación');
  } else {
    alert('❌ Error al abrir bulto: ' + error.message);
  }
}
```

---

## 💡 Casos de Uso

### 1. **Venta por Peso Variable**
Cliente quiere comprar exactamente 300g de un producto que solo viene en paquetes de 500g.

**Solución:** Abrir 1 paquete a granel y vender 300g.

### 2. **Optimizar Inventario**
Tienes 1 paquete viejo que quieres vender rápido antes de que expire.

**Solución:** Abrir a granel para ofrecer descuentos por unidad suelta.

### 3. **Flexibilidad al Cliente**
Permitir que los clientes compren en cantidades personalizadas.

**Solución:** Mantener stock empaquetado y a granel simultáneamente.

---

## ✅ Checklist de Implementación

- [ ] Crear servicio `openBulkConversion` en `bulkConversionService.ts`
- [ ] Crear hook `useBulkConversion`
- [ ] Implementar componente `BulkConversionModal`
- [ ] Agregar estilos CSS para el modal
- [ ] Integrar botón "Abrir para Granel" en tabla de inventario
- [ ] Implementar carga de presentaciones granel
- [ ] Agregar validaciones (stock disponible, permisos)
- [ ] Implementar manejo de errores
- [ ] Probar conversión completa
- [ ] Verificar que el stock se actualiza correctamente

---

## 🎯 Ventajas del Sistema

✅ **Flexibilidad de Venta**: Vender empaquetado o a granel según necesidad  
✅ **Control de Inventario**: Rastrear qué paquetes están abiertos  
✅ **FIFO Automático**: Sistema usa primero el stock a granel antes de abrir nuevos paquetes  
✅ **Trazabilidad**: Cada conversión queda registrada con fecha y cantidad  
✅ **Optimización**: Reducir desperdicios vendiendo productos sueltos  

---

## 📞 Soporte

Si tienes dudas:
1. Verifica que el usuario tenga permisos `PRODUCTS:UPDATE`
2. Confirma que hay paquetes disponibles (`quantity_available >= converted_quantity`)
3. Asegúrate de tener una presentación tipo "granel" creada
4. Revisa que `converted_quantity` y `unit_conversion_factor` sean números enteros positivos
5. Verifica que el cálculo: `converted_quantity × unit_conversion_factor` produzca el total esperado

---

**¡Sistema de conversión a granel listo para implementar! 🎉**
