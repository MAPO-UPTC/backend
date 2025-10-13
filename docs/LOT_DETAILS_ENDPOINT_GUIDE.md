# Guía Completa: Endpoint de Detalles de Lotes por Presentación

## 📋 Índice

1. [Introducción](#introducción)
2. [Endpoint de API](#endpoint-de-api)
3. [Casos de Uso](#casos-de-uso)
4. [Integración en Frontend](#integración-en-frontend)
5. [Ejemplos TypeScript](#ejemplos-typescript)
6. [Componente React Completo](#componente-react-completo)
7. [Validaciones y Manejo de Errores](#validaciones-y-manejo-de-errores)

---

## 🎯 Introducción

Este endpoint proporciona **detalles completos de todos los lotes** asociados a una presentación específica de producto. Es fundamental para:

- ✅ **Conversión de empaquetado a granel**: Obtener el lote más antiguo (FIFO)
- ✅ **Visualización de distribución de stock**: Mostrar cómo se distribuye el inventario
- ✅ **Trazabilidad**: Seguimiento de fechas de recepción, vencimiento y lotes
- ✅ **Gestión de inventario avanzada**: Tomar decisiones basadas en antigüedad del stock

**¿Por qué este endpoint?**

El endpoint existente `GET /inventory/stock/{presentation_id}` solo retorna un número entero (cantidad total disponible). Para implementar funcionalidades avanzadas como la conversión a granel, necesitamos:

- Lista completa de lotes (no solo el total)
- Información del producto y presentación
- Fechas de recepción y vencimiento
- Ordenamiento FIFO automático
- ID del lote más antiguo para operaciones

---

## 🔌 Endpoint de API

### GET `/inventory/presentations/{presentation_id}/lot-details`

Obtiene todos los detalles de lotes para una presentación específica, ordenados por FIFO.

#### **Parámetros**

| Parámetro | Tipo | Ubicación | Requerido | Descripción |
|-----------|------|-----------|-----------|-------------|
| `presentation_id` | UUID | Path | ✅ Sí | ID de la presentación del producto |
| `available_only` | boolean | Query | ❌ No | Si `true`, solo retorna lotes con stock disponible (default: `true`) |

#### **Headers Requeridos**

```typescript
{
  "Authorization": "Bearer <token_jwt>"
}
```

#### **Respuesta Exitosa (200 OK)**

```json
{
  "success": true,
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "lot_id": "123e4567-e89b-12d3-a456-426614174001",
      "presentation_id": "123e4567-e89b-12d3-a456-426614174002",
      "quantity_received": 100,
      "quantity_available": 75,
      "unit_cost": 15.50,
      "batch_number": "BATCH-2024-001",
      "lot_code": "LOT-2024-001",
      "received_date": "2024-01-15T10:30:00",
      "expiry_date": "2025-01-15T23:59:59",
      "lot_status": "ACTIVE",
      "product_id": "123e4567-e89b-12d3-a456-426614174003",
      "product_name": "Acetaminofén",
      "presentation_name": "Caja x100 tabletas",
      "presentation_unit": "caja"
    },
    {
      "id": "123e4567-e89b-12d3-a456-426614174004",
      "lot_id": "123e4567-e89b-12d3-a456-426614174005",
      "presentation_id": "123e4567-e89b-12d3-a456-426614174002",
      "quantity_received": 50,
      "quantity_available": 30,
      "unit_cost": 16.00,
      "batch_number": "BATCH-2024-002",
      "lot_code": "LOT-2024-002",
      "received_date": "2024-02-10T14:20:00",
      "expiry_date": "2025-02-10T23:59:59",
      "lot_status": "ACTIVE",
      "product_id": "123e4567-e89b-12d3-a456-426614174003",
      "product_name": "Acetaminofén",
      "presentation_name": "Caja x100 tabletas",
      "presentation_unit": "caja"
    }
  ],
  "count": 2,
  "metadata": {
    "presentation_id": "123e4567-e89b-12d3-a456-426614174002",
    "total_available_quantity": 105,
    "oldest_lot_date": "2024-01-15T10:30:00",
    "newest_lot_date": "2024-02-10T14:20:00"
  }
}
```

#### **Estructura de Respuesta**

##### Campo `data[]` - Array de Lotes

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | ID único del detalle de lote (lot_detail_id) |
| `lot_id` | UUID | ID del lote al que pertenece |
| `presentation_id` | UUID | ID de la presentación del producto |
| `quantity_received` | number | Cantidad total recibida en este lote |
| `quantity_available` | number | Cantidad disponible actualmente |
| `unit_cost` | number | Costo unitario del producto en este lote |
| `batch_number` | string | Número de lote/batch del proveedor |
| `lot_code` | string | Código interno del lote |
| `received_date` | ISO 8601 | Fecha de recepción del lote |
| `expiry_date` | ISO 8601 | Fecha de vencimiento del lote |
| `lot_status` | string | Estado del lote: `ACTIVE`, `EXPIRED`, etc. |
| `product_id` | UUID | ID del producto |
| `product_name` | string | Nombre del producto |
| `presentation_name` | string | Nombre de la presentación |
| `presentation_unit` | string | Unidad de medida de la presentación |

##### Campo `metadata` - Información Agregada

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `presentation_id` | UUID | ID de la presentación consultada |
| `total_available_quantity` | number | Suma total de stock disponible |
| `oldest_lot_date` | ISO 8601 | Fecha del lote más antiguo (FIFO - primero en salir) |
| `newest_lot_date` | ISO 8601 | Fecha del lote más nuevo |

#### **Respuestas de Error**

##### 400 Bad Request - UUID Inválido
```json
{
  "detail": "El ID de presentación 'abc123' no es un UUID válido"
}
```

##### 404 Not Found - Sin Lotes Disponibles
```json
{
  "detail": "No hay lotes disponibles para la presentación 123e4567-e89b-12d3-a456-426614174002"
}
```

##### 500 Internal Server Error
```json
{
  "detail": "Error obteniendo detalles de lotes: <mensaje de error>"
}
```

---

## 💼 Casos de Uso

### 1. **Conversión de Empaquetado a Granel (Principal)**

**Escenario**: Un usuario necesita abrir una caja de 100 tabletas para vender tabletas sueltas.

**Flujo**:
1. Usuario selecciona presentación empaquetada (ej: "Caja x100 tabletas")
2. Frontend llama al endpoint para obtener lista de lotes
3. Se obtiene el **primer lote** de la lista (más antiguo, FIFO)
4. Se muestra modal con información del lote a convertir
5. Se llama a `POST /products/open-bulk/` con el `lot_detail_id` del lote más antiguo

```typescript
// Ejemplo de flujo
const lotDetails = await getLotDetails(presentationId);
const oldestLot = lotDetails.data[0]; // Primera posición = más antiguo (FIFO)

// Mostrar en UI
console.log(`Lote más antiguo: ${oldestLot.lot_code}`);
console.log(`Recibido: ${formatDate(oldestLot.received_date)}`);
console.log(`Disponible: ${oldestLot.quantity_available} ${oldestLot.presentation_unit}`);

// Proceder con conversión
await openBulkConversion({
  lot_detail_id: oldestLot.id,
  converted_quantity: 1,
  unit_conversion_factor: 100
});
```

### 2. **Visualización de Distribución de Stock**

**Escenario**: Administrador quiere ver cómo está distribuido el inventario de un producto.

```typescript
const lotDetails = await getLotDetails(presentationId);

// Mostrar tabla con todos los lotes
lotDetails.data.forEach(lot => {
  console.log(`
    Lote: ${lot.lot_code}
    Recibido: ${formatDate(lot.received_date)}
    Disponible: ${lot.quantity_available}
    Vence: ${formatDate(lot.expiry_date)}
  `);
});

// Mostrar metadata
console.log(`Total disponible: ${lotDetails.metadata.total_available_quantity}`);
```

### 3. **Alertas de Vencimiento**

**Escenario**: Mostrar alertas de lotes próximos a vencer.

```typescript
const lotDetails = await getLotDetails(presentationId, false); // Incluir todos

const expiringLots = lotDetails.data.filter(lot => {
  const daysUntilExpiry = getDaysDifference(new Date(), new Date(lot.expiry_date));
  return daysUntilExpiry > 0 && daysUntilExpiry <= 30; // Vence en 30 días o menos
});

if (expiringLots.length > 0) {
  showAlert(`${expiringLots.length} lote(s) próximos a vencer`);
}
```

### 4. **Análisis de Rotación de Inventario**

**Escenario**: Calcular antigüedad promedio del stock.

```typescript
const lotDetails = await getLotDetails(presentationId);

const averageAge = lotDetails.data.reduce((sum, lot) => {
  const ageInDays = getDaysDifference(new Date(lot.received_date), new Date());
  return sum + ageInDays;
}, 0) / lotDetails.data.length;

console.log(`Edad promedio del inventario: ${averageAge.toFixed(0)} días`);
```

---

## 🚀 Integración en Frontend

### TypeScript - Interfaces y Tipos

```typescript
// interfaces/inventory.ts

/**
 * Representa un detalle de lote individual con información completa
 */
export interface ILotDetail {
  // Información del LotDetail
  id: string;                      // lot_detail_id - usar para conversiones
  lot_id: string;                  // ID del lote
  presentation_id: string;         // ID de la presentación
  quantity_received: number;       // Cantidad recibida inicialmente
  quantity_available: number;      // Cantidad disponible ahora
  unit_cost: number;               // Costo unitario
  batch_number: string;            // Número de lote del proveedor
  
  // Información del Lote
  lot_code: string;                // Código interno del lote
  received_date: string;           // ISO 8601 - fecha de recepción
  expiry_date: string;             // ISO 8601 - fecha de vencimiento
  lot_status: string;              // ACTIVE, EXPIRED, etc.
  
  // Información del Producto
  product_id: string;              // ID del producto
  product_name: string;            // Nombre del producto
  presentation_name: string;       // Nombre de la presentación
  presentation_unit: string;       // Unidad de medida
}

/**
 * Metadata agregada sobre los lotes
 */
export interface ILotDetailsMetadata {
  presentation_id: string;         // ID de la presentación consultada
  total_available_quantity: number;// Total de stock disponible
  oldest_lot_date: string;         // ISO 8601 - lote más antiguo
  newest_lot_date: string;         // ISO 8601 - lote más nuevo
}

/**
 * Respuesta completa del endpoint
 */
export interface ILotDetailsResponse {
  success: boolean;
  data: ILotDetail[];              // Array de lotes, ordenados por FIFO
  count: number;                   // Cantidad de lotes
  metadata: ILotDetailsMetadata;   // Información agregada
}
```

### Servicio de API

```typescript
// services/inventoryService.ts

import axios from 'axios';
import { ILotDetailsResponse } from '../interfaces/inventory';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class InventoryService {
  /**
   * Obtiene los detalles de todos los lotes para una presentación específica
   * 
   * @param presentationId - UUID de la presentación
   * @param availableOnly - Si true, solo retorna lotes con stock disponible
   * @returns Promesa con la respuesta de lotes
   * 
   * @throws Error si el presentationId es inválido
   * @throws Error si no hay lotes disponibles (404)
   * @throws Error si falla la petición (500)
   * 
   * @example
   * ```typescript
   * const lotDetails = await inventoryService.getLotDetailsByPresentation(
   *   '123e4567-e89b-12d3-a456-426614174002',
   *   true
   * );
   * 
   * // Obtener lote más antiguo (FIFO)
   * const oldestLot = lotDetails.data[0];
   * ```
   */
  async getLotDetailsByPresentation(
    presentationId: string,
    availableOnly: boolean = true
  ): Promise<ILotDetailsResponse> {
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        throw new Error('No hay token de autenticación disponible');
      }

      // Validar UUID antes de hacer la petición
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
      if (!uuidRegex.test(presentationId)) {
        throw new Error(`El ID de presentación '${presentationId}' no es un UUID válido`);
      }

      const response = await axios.get<ILotDetailsResponse>(
        `${API_BASE_URL}/inventory/presentations/${presentationId}/lot-details`,
        {
          params: {
            available_only: availableOnly
          },
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const detail = error.response?.data?.detail;

        if (status === 404) {
          throw new Error(detail || 'No hay lotes disponibles para esta presentación');
        } else if (status === 400) {
          throw new Error(detail || 'ID de presentación inválido');
        } else if (status === 500) {
          throw new Error('Error del servidor al obtener detalles de lotes');
        } else {
          throw new Error(`Error en la petición: ${detail || error.message}`);
        }
      }
      throw error;
    }
  }

  /**
   * Obtiene el lote más antiguo (FIFO) para una presentación
   * 
   * @param presentationId - UUID de la presentación
   * @returns El lote más antiguo o null si no hay lotes
   * 
   * @example
   * ```typescript
   * const oldestLot = await inventoryService.getOldestLot(presentationId);
   * if (oldestLot) {
   *   console.log(`Usar lote: ${oldestLot.lot_code}`);
   * }
   * ```
   */
  async getOldestLot(presentationId: string): Promise<ILotDetail | null> {
    const response = await this.getLotDetailsByPresentation(presentationId, true);
    return response.data.length > 0 ? response.data[0] : null;
  }

  /**
   * Calcula el total de stock disponible para una presentación
   * (Alternativa al endpoint /stock/{presentation_id})
   * 
   * @param presentationId - UUID de la presentación
   * @returns Cantidad total disponible
   */
  async getTotalAvailableStock(presentationId: string): Promise<number> {
    const response = await this.getLotDetailsByPresentation(presentationId, true);
    return response.metadata.total_available_quantity;
  }
}

export const inventoryService = new InventoryService();
```

### Custom Hook React

```typescript
// hooks/useLotDetails.ts

import { useState, useEffect } from 'react';
import { inventoryService } from '../services/inventoryService';
import { ILotDetail, ILotDetailsMetadata } from '../interfaces/inventory';

interface UseLotDetailsOptions {
  presentationId: string | null;
  availableOnly?: boolean;
  autoFetch?: boolean;
}

interface UseLotDetailsReturn {
  lotDetails: ILotDetail[];
  metadata: ILotDetailsMetadata | null;
  oldestLot: ILotDetail | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Hook personalizado para manejar detalles de lotes
 * 
 * @param options - Opciones de configuración
 * @returns Estado y funciones para manejar los lotes
 * 
 * @example
 * ```typescript
 * const { lotDetails, oldestLot, loading } = useLotDetails({
 *   presentationId: selectedPresentation?.id || null,
 *   availableOnly: true,
 *   autoFetch: true
 * });
 * 
 * if (oldestLot) {
 *   return <div>Lote más antiguo: {oldestLot.lot_code}</div>;
 * }
 * ```
 */
export const useLotDetails = (options: UseLotDetailsOptions): UseLotDetailsReturn => {
  const { presentationId, availableOnly = true, autoFetch = true } = options;

  const [lotDetails, setLotDetails] = useState<ILotDetail[]>([]);
  const [metadata, setMetadata] = useState<ILotDetailsMetadata | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLotDetails = async () => {
    if (!presentationId) {
      setLotDetails([]);
      setMetadata(null);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await inventoryService.getLotDetailsByPresentation(
        presentationId,
        availableOnly
      );

      setLotDetails(response.data);
      setMetadata(response.metadata);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      setLotDetails([]);
      setMetadata(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (autoFetch) {
      fetchLotDetails();
    }
  }, [presentationId, availableOnly, autoFetch]);

  // Calcular lote más antiguo (primera posición = FIFO)
  const oldestLot = lotDetails.length > 0 ? lotDetails[0] : null;

  return {
    lotDetails,
    metadata,
    oldestLot,
    loading,
    error,
    refetch: fetchLotDetails
  };
};
```

---

## 🎨 Componente React Completo

### Componente: Tabla de Detalles de Lotes

```typescript
// components/LotDetailsTable.tsx

import React from 'react';
import { useLotDetails } from '../hooks/useLotDetails';
import { ILotDetail } from '../interfaces/inventory';
import './LotDetailsTable.css';

interface LotDetailsTableProps {
  presentationId: string;
  onLotSelect?: (lot: ILotDetail) => void;
  showActions?: boolean;
}

/**
 * Componente para mostrar tabla de detalles de lotes
 * Muestra todos los lotes ordenados por FIFO (más antiguo primero)
 */
export const LotDetailsTable: React.FC<LotDetailsTableProps> = ({
  presentationId,
  onLotSelect,
  showActions = false
}) => {
  const { lotDetails, metadata, loading, error } = useLotDetails({
    presentationId,
    availableOnly: true,
    autoFetch: true
  });

  /**
   * Formatea fecha ISO a formato legible
   */
  const formatDate = (isoDate: string): string => {
    const date = new Date(isoDate);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  /**
   * Calcula días hasta vencimiento
   */
  const getDaysUntilExpiry = (expiryDate: string): number => {
    const now = new Date();
    const expiry = new Date(expiryDate);
    const diffTime = expiry.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  /**
   * Retorna clase CSS según días hasta vencimiento
   */
  const getExpiryClass = (expiryDate: string): string => {
    const days = getDaysUntilExpiry(expiryDate);
    if (days < 0) return 'expired';
    if (days <= 30) return 'expiring-soon';
    if (days <= 90) return 'expiring-warning';
    return 'expiring-ok';
  };

  if (loading) {
    return (
      <div className="lot-details-loading">
        <div className="spinner"></div>
        <p>Cargando detalles de lotes...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="lot-details-error">
        <span className="error-icon">⚠️</span>
        <p>{error}</p>
      </div>
    );
  }

  if (lotDetails.length === 0) {
    return (
      <div className="lot-details-empty">
        <span className="empty-icon">📦</span>
        <p>No hay lotes disponibles para esta presentación</p>
      </div>
    );
  }

  return (
    <div className="lot-details-container">
      {/* Metadata Summary */}
      <div className="lot-details-summary">
        <div className="summary-card">
          <span className="summary-label">Total Disponible</span>
          <span className="summary-value">
            {metadata?.total_available_quantity} unidades
          </span>
        </div>
        <div className="summary-card">
          <span className="summary-label">Lotes Activos</span>
          <span className="summary-value">{lotDetails.length}</span>
        </div>
        <div className="summary-card">
          <span className="summary-label">Lote Más Antiguo</span>
          <span className="summary-value">
            {metadata?.oldest_lot_date ? formatDate(metadata.oldest_lot_date) : '-'}
          </span>
        </div>
      </div>

      {/* Tabla de Lotes */}
      <div className="lot-details-table-wrapper">
        <table className="lot-details-table">
          <thead>
            <tr>
              <th>FIFO</th>
              <th>Código Lote</th>
              <th>Batch</th>
              <th>Recibido</th>
              <th>Vencimiento</th>
              <th>Disponible</th>
              <th>Costo Unit.</th>
              <th>Estado</th>
              {showActions && <th>Acciones</th>}
            </tr>
          </thead>
          <tbody>
            {lotDetails.map((lot, index) => {
              const daysUntilExpiry = getDaysUntilExpiry(lot.expiry_date);
              const expiryClass = getExpiryClass(lot.expiry_date);

              return (
                <tr key={lot.id} className={index === 0 ? 'oldest-lot' : ''}>
                  {/* Indicador FIFO */}
                  <td className="fifo-indicator">
                    {index === 0 ? (
                      <span className="badge badge-primary" title="Lote más antiguo - usar primero">
                        🔄 FIFO #1
                      </span>
                    ) : (
                      <span className="badge badge-secondary">#{index + 1}</span>
                    )}
                  </td>

                  {/* Código de Lote */}
                  <td className="lot-code">
                    <strong>{lot.lot_code}</strong>
                  </td>

                  {/* Batch Number */}
                  <td className="batch-number">{lot.batch_number}</td>

                  {/* Fecha de Recepción */}
                  <td className="received-date">
                    {formatDate(lot.received_date)}
                  </td>

                  {/* Fecha de Vencimiento con Indicador */}
                  <td className={`expiry-date ${expiryClass}`}>
                    <div className="expiry-info">
                      <span>{formatDate(lot.expiry_date)}</span>
                      <small>
                        {daysUntilExpiry < 0
                          ? `Vencido hace ${Math.abs(daysUntilExpiry)} días`
                          : `${daysUntilExpiry} días`}
                      </small>
                    </div>
                  </td>

                  {/* Cantidad Disponible */}
                  <td className="quantity-available">
                    <strong>{lot.quantity_available}</strong>
                    <small>de {lot.quantity_received}</small>
                  </td>

                  {/* Costo Unitario */}
                  <td className="unit-cost">
                    ${lot.unit_cost.toFixed(2)}
                  </td>

                  {/* Estado */}
                  <td className="lot-status">
                    <span className={`status-badge status-${lot.lot_status.toLowerCase()}`}>
                      {lot.lot_status}
                    </span>
                  </td>

                  {/* Acciones */}
                  {showActions && (
                    <td className="lot-actions">
                      <button
                        className="btn btn-sm btn-primary"
                        onClick={() => onLotSelect?.(lot)}
                        disabled={lot.quantity_available <= 0}
                      >
                        Usar
                      </button>
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
```

### Estilos CSS

```css
/* components/LotDetailsTable.css */

.lot-details-container {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

/* Summary Cards */
.lot-details-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.summary-card {
  background-color: white;
  padding: 15px;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.summary-label {
  font-size: 0.875rem;
  color: #6c757d;
  margin-bottom: 5px;
}

.summary-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #212529;
}

/* Table Styles */
.lot-details-table-wrapper {
  overflow-x: auto;
  background-color: white;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.lot-details-table {
  width: 100%;
  border-collapse: collapse;
}

.lot-details-table thead {
  background-color: #e9ecef;
}

.lot-details-table th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  font-size: 0.875rem;
  color: #495057;
  text-transform: uppercase;
}

.lot-details-table td {
  padding: 12px;
  border-bottom: 1px solid #dee2e6;
}

.lot-details-table tbody tr:hover {
  background-color: #f8f9fa;
}

/* Oldest Lot Highlight */
.lot-details-table tbody tr.oldest-lot {
  background-color: #e7f3ff;
  border-left: 4px solid #007bff;
}

/* FIFO Indicator */
.fifo-indicator {
  text-align: center;
}

.badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-primary {
  background-color: #007bff;
  color: white;
}

.badge-secondary {
  background-color: #6c757d;
  color: white;
}

/* Expiry Date Colors */
.expiry-date {
  font-weight: 500;
}

.expiry-date.expiring-ok {
  color: #28a745;
}

.expiry-date.expiring-warning {
  color: #ffc107;
}

.expiry-date.expiring-soon {
  color: #fd7e14;
}

.expiry-date.expired {
  color: #dc3545;
  font-weight: 700;
}

.expiry-info {
  display: flex;
  flex-direction: column;
}

.expiry-info small {
  font-size: 0.75rem;
  margin-top: 2px;
}

/* Status Badge */
.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-active {
  background-color: #d4edda;
  color: #155724;
}

.status-expired {
  background-color: #f8d7da;
  color: #721c24;
}

/* Loading State */
.lot-details-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error State */
.lot-details-error {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px;
  background-color: #f8d7da;
  color: #721c24;
  border-radius: 6px;
}

.error-icon {
  font-size: 1.5rem;
}

/* Empty State */
.lot-details-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #6c757d;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 10px;
}
```

---

## ✅ Validaciones y Manejo de Errores

### Frontend - Validaciones antes de llamar al endpoint

```typescript
// utils/validators.ts

/**
 * Valida que un string sea un UUID válido
 */
export const isValidUUID = (uuid: string): boolean => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
};

/**
 * Valida presentationId antes de llamar al endpoint
 */
export const validatePresentationId = (presentationId: string | null): void => {
  if (!presentationId) {
    throw new Error('El ID de presentación es requerido');
  }

  if (!isValidUUID(presentationId)) {
    throw new Error(`El ID de presentación '${presentationId}' no es un UUID válido`);
  }
};

// Uso en componente
try {
  validatePresentationId(selectedPresentation?.id);
  const lotDetails = await inventoryService.getLotDetailsByPresentation(
    selectedPresentation!.id
  );
} catch (error) {
  console.error('Error de validación:', error.message);
}
```

### Manejo de Estados de Error

```typescript
// components/LotDetailsWithErrors.tsx

import React, { useState, useEffect } from 'react';
import { inventoryService } from '../services/inventoryService';
import { ILotDetail } from '../interfaces/inventory';

export const LotDetailsWithErrors: React.FC<{ presentationId: string }> = ({
  presentationId
}) => {
  const [lotDetails, setLotDetails] = useState<ILotDetail[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<{
    type: 'validation' | 'not_found' | 'server' | 'network';
    message: string;
  } | null>(null);

  useEffect(() => {
    const fetchLots = async () => {
      setLoading(true);
      setError(null);

      try {
        // Validación previa
        if (!presentationId) {
          throw new Error('ID de presentación no proporcionado');
        }

        const response = await inventoryService.getLotDetailsByPresentation(
          presentationId
        );

        setLotDetails(response.data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Error desconocido';

        // Clasificar tipo de error
        if (errorMessage.includes('UUID')) {
          setError({ type: 'validation', message: errorMessage });
        } else if (errorMessage.includes('No hay lotes')) {
          setError({ type: 'not_found', message: errorMessage });
        } else if (errorMessage.includes('servidor')) {
          setError({ type: 'server', message: errorMessage });
        } else {
          setError({ type: 'network', message: errorMessage });
        }
      } finally {
        setLoading(false);
      }
    };

    fetchLots();
  }, [presentationId]);

  // Renderizar según tipo de error
  if (error) {
    switch (error.type) {
      case 'validation':
        return (
          <div className="alert alert-warning">
            <strong>Validación:</strong> {error.message}
          </div>
        );
      case 'not_found':
        return (
          <div className="alert alert-info">
            <strong>Sin lotes:</strong> {error.message}
          </div>
        );
      case 'server':
        return (
          <div className="alert alert-danger">
            <strong>Error del servidor:</strong> {error.message}
            <button onClick={() => window.location.reload()}>Reintentar</button>
          </div>
        );
      case 'network':
        return (
          <div className="alert alert-danger">
            <strong>Error de conexión:</strong> {error.message}
          </div>
        );
    }
  }

  // Renderizar tabla normal
  return (
    <div>
      {/* Renderizar tabla de lotes */}
    </div>
  );
};
```

---

## 📚 Resumen de Integración

### Flujo Completo: Conversión de Empaquetado a Granel

```typescript
// Flujo completo paso a paso

// 1. Usuario selecciona presentación empaquetada
const selectedPresentation = {
  id: '123e4567-e89b-12d3-a456-426614174002',
  name: 'Caja x100 tabletas',
  product_id: '123e4567-e89b-12d3-a456-426614174003'
};

// 2. Obtener detalles de lotes (ordenados por FIFO)
const { lotDetails, oldestLot } = useLotDetails({
  presentationId: selectedPresentation.id,
  availableOnly: true
});

// 3. Mostrar información del lote más antiguo al usuario
if (oldestLot) {
  console.log(`
    Lote a usar: ${oldestLot.lot_code}
    Recibido: ${formatDate(oldestLot.received_date)}
    Disponible: ${oldestLot.quantity_available} cajas
    Contiene: ${oldestLot.quantity_available * 100} tabletas totales
  `);
}

// 4. Usuario confirma conversión (ej: abrir 1 caja)
const conversionData = {
  lot_detail_id: oldestLot.id,          // ID del lote más antiguo
  converted_quantity: 1,                 // 1 caja
  unit_conversion_factor: 100            // 100 tabletas por caja
};

// 5. Llamar endpoint de conversión
const result = await productService.openBulkConversion(conversionData);

// 6. Resultado:
// - Se descuenta 1 caja del lote antiguo
// - Se agregan 100 tabletas sueltas en presentación granel
// - Frontend actualiza inventario

// 7. Refrescar lista de lotes
refetch();
```

---

## 🎯 Puntos Clave

1. ✅ **FIFO Automático**: Los lotes vienen ordenados por fecha de recepción (más antiguo primero)
2. ✅ **Primer Elemento = Más Antiguo**: Siempre usar `lotDetails.data[0]` para conversiones
3. ✅ **Información Completa**: No necesitas llamar endpoints adicionales para producto/presentación
4. ✅ **Metadata Útil**: Incluye totales y fechas extremas para análisis
5. ✅ **Validaciones**: Backend valida UUID y existencia de lotes
6. ✅ **Filtrado Opcional**: Puedes incluir lotes sin stock con `available_only=false`

---

## 📞 Soporte

Para más información sobre:
- **Conversión a granel**: Ver `BULK_CONVERSION_GUIDE.md`
- **Diagramas de flujo**: Ver `BULK_CONVERSION_DIAGRAM.md`
- **Resumen ejecutivo**: Ver `BULK_CONVERSION_SUMMARY.md`

---

**Última actualización**: Enero 2025
**Versión de API**: v1.0
**Autor**: Backend Team MAPO
