# 📋 Endpoint de Detalles de Venta - Guía para Frontend

## 📌 Descripción General

Este endpoint permite obtener **información completa y detallada** de una venta específica, incluyendo datos del cliente, vendedor, productos vendidos con sus nombres y precios de costo.

---

## 🔗 Endpoint

### **GET** `/sales/{sale_id}/details`

Obtiene los detalles completos de una venta por su ID.

---

## 🔐 Autenticación

**Requiere autenticación con Bearer Token:**

```typescript
headers: {
  'Authorization': `Bearer ${token}`
}
```

---

## 📥 Parámetros

### Path Parameters

| Parámetro | Tipo   | Requerido | Descripción           |
|-----------|--------|-----------|----------------------|
| `sale_id` | string (UUID) | ✅ Sí | ID de la venta a consultar |

### Ejemplo de Request

```typescript
const saleId = "550e8400-e29b-41d4-a716-446655440000";
const url = `http://localhost:8000/sales/${saleId}/details`;
```

---

## 📤 Respuesta

### Estructura de la Respuesta

```typescript
interface SaleDetailExtended {
  id: string;                    // UUID del detalle
  sale_id: string;               // UUID de la venta
  presentation_id: string;       // UUID de la presentación
  lot_detail_id: string | null;  // UUID del lote (null si es granel)
  bulk_conversion_id: string | null; // UUID conversión granel (null si es empaquetado)
  quantity: number;              // Cantidad vendida
  unit_price: number;            // Precio de venta unitario
  line_total: number;            // Total de la línea (quantity × unit_price)
  
  // ✨ Información adicional del producto
  product_name: string;          // Nombre del producto
  presentation_name: string;     // Nombre de la presentación
  cost_price: number;            // Precio de costo del producto
}

interface SaleDetailFullResponse {
  id: string;                    // UUID de la venta
  sale_code: string;             // Código único de venta
  sale_date: string;             // Fecha ISO 8601
  customer_id: string;           // UUID del cliente
  user_id: string;               // UUID del vendedor
  total: number;                 // Total de la venta
  status: string;                // Estado: "completed", "cancelled", etc.
  
  // 👤 Información del cliente
  customer_name: string;         // Nombre completo del cliente
  customer_document: string;     // Tipo y número de documento
  
  // 👨‍💼 Información del vendedor
  seller_name: string;           // Nombre completo del vendedor
  
  // 📦 Items de la venta
  items: SaleDetailExtended[];   // Array de items con detalles extendidos
}
```

---

## 📋 Ejemplo de Respuesta Completa

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "sale_code": "VEN-20251012120530",
  "sale_date": "2025-10-12T12:05:30",
  "customer_id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "770e8400-e29b-41d4-a716-446655440002",
  "total": 87.50,
  "status": "completed",
  
  "customer_name": "Juan Carlos Pérez",
  "customer_document": "CC: 1234567890",
  
  "seller_name": "María García López",
  
  "items": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "sale_id": "550e8400-e29b-41d4-a716-446655440000",
      "presentation_id": "990e8400-e29b-41d4-a716-446655440004",
      "lot_detail_id": "aa0e8400-e29b-41d4-a716-446655440005",
      "bulk_conversion_id": null,
      "quantity": 3,
      "unit_price": 15.50,
      "line_total": 46.50,
      "product_name": "Arroz Diana",
      "presentation_name": "Paquete x 500g",
      "cost_price": 10.20
    },
    {
      "id": "bb0e8400-e29b-41d4-a716-446655440006",
      "sale_id": "550e8400-e29b-41d4-a716-446655440000",
      "presentation_id": "cc0e8400-e29b-41d4-a716-446655440007",
      "lot_detail_id": null,
      "bulk_conversion_id": "dd0e8400-e29b-41d4-a716-446655440008",
      "quantity": 2,
      "unit_price": 20.50,
      "line_total": 41.00,
      "product_name": "Azúcar Manuelita",
      "presentation_name": "Bolsa x 1kg",
      "cost_price": 14.80
    }
  ]
}
```

---

## 🚀 Implementación en Frontend

### 1. **Servicio API** (TypeScript)

```typescript
// services/salesService.ts
import axios from 'axios';

const API_URL = 'http://localhost:8000';

interface SaleDetailExtended {
  id: string;
  sale_id: string;
  presentation_id: string;
  lot_detail_id: string | null;
  bulk_conversion_id: string | null;
  quantity: number;
  unit_price: number;
  line_total: number;
  product_name: string;
  presentation_name: string;
  cost_price: number;
}

interface SaleDetailFullResponse {
  id: string;
  sale_code: string;
  sale_date: string;
  customer_id: string;
  user_id: string;
  total: number;
  status: string;
  customer_name: string;
  customer_document: string;
  seller_name: string;
  items: SaleDetailExtended[];
}

export const getSaleDetails = async (
  saleId: string,
  token: string
): Promise<SaleDetailFullResponse> => {
  try {
    const response = await axios.get(
      `${API_URL}/sales/${saleId}/details`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 404) {
        throw new Error('Venta no encontrada');
      }
      throw new Error(error.response?.data?.detail || 'Error al obtener detalles de la venta');
    }
    throw error;
  }
};
```

---

### 2. **Hook Personalizado** (React)

```typescript
// hooks/useSaleDetails.ts
import { useState, useEffect } from 'react';
import { getSaleDetails } from '../services/salesService';

interface UseSaleDetailsOptions {
  saleId: string | null;
  token: string;
  autoFetch?: boolean; // Si debe cargar automáticamente
}

export const useSaleDetails = ({ 
  saleId, 
  token, 
  autoFetch = true 
}: UseSaleDetailsOptions) => {
  const [saleDetails, setSaleDetails] = useState<SaleDetailFullResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSaleDetails = async (id?: string) => {
    const targetId = id || saleId;
    
    if (!targetId) {
      setError('ID de venta no proporcionado');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await getSaleDetails(targetId, token);
      setSaleDetails(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      setSaleDetails(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (autoFetch && saleId) {
      fetchSaleDetails();
    }
  }, [saleId, autoFetch]);

  return {
    saleDetails,
    loading,
    error,
    refetch: fetchSaleDetails
  };
};
```

---

### 3. **Componente de Detalles de Venta** (React)

```typescript
// components/SaleDetailsModal.tsx
import React from 'react';
import { useSaleDetails } from '../hooks/useSaleDetails';

interface SaleDetailsModalProps {
  saleId: string;
  onClose: () => void;
}

export const SaleDetailsModal: React.FC<SaleDetailsModalProps> = ({ 
  saleId, 
  onClose 
}) => {
  const token = localStorage.getItem('authToken') || '';
  const { saleDetails, loading, error } = useSaleDetails({ 
    saleId, 
    token,
    autoFetch: true 
  });

  if (loading) {
    return (
      <div className="modal-overlay">
        <div className="modal-content">
          <h2>Cargando detalles...</h2>
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="modal-overlay">
        <div className="modal-content error">
          <h2>❌ Error</h2>
          <p>{error}</p>
          <button onClick={onClose}>Cerrar</button>
        </div>
      </div>
    );
  }

  if (!saleDetails) {
    return null;
  }

  // Calcular margen de ganancia total
  const totalCost = saleDetails.items.reduce(
    (sum, item) => sum + (item.cost_price * item.quantity), 
    0
  );
  const totalProfit = saleDetails.total - totalCost;
  const profitMargin = ((totalProfit / saleDetails.total) * 100).toFixed(2);

  return (
    <div className="modal-overlay">
      <div className="modal-content sale-details-modal">
        {/* Header */}
        <div className="modal-header">
          <h2>📋 Detalles de Venta</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        {/* Información General */}
        <div className="sale-info-section">
          <div className="info-row">
            <span className="label">Código de Venta:</span>
            <span className="value">{saleDetails.sale_code}</span>
          </div>
          <div className="info-row">
            <span className="label">Fecha:</span>
            <span className="value">
              {new Date(saleDetails.sale_date).toLocaleString('es-CO')}
            </span>
          </div>
          <div className="info-row">
            <span className="label">Estado:</span>
            <span className={`badge ${saleDetails.status}`}>
              {saleDetails.status}
            </span>
          </div>
        </div>

        {/* Información de Cliente */}
        <div className="customer-section">
          <h3>👤 Cliente</h3>
          <p><strong>Nombre:</strong> {saleDetails.customer_name}</p>
          <p><strong>Documento:</strong> {saleDetails.customer_document}</p>
        </div>

        {/* Información de Vendedor */}
        <div className="seller-section">
          <h3>👨‍💼 Vendedor</h3>
          <p>{saleDetails.seller_name}</p>
        </div>

        {/* Tabla de Items */}
        <div className="items-section">
          <h3>📦 Productos Vendidos</h3>
          <table className="items-table">
            <thead>
              <tr>
                <th>Producto</th>
                <th>Presentación</th>
                <th>Cant.</th>
                <th>P. Costo</th>
                <th>P. Venta</th>
                <th>Subtotal</th>
                <th>Margen</th>
              </tr>
            </thead>
            <tbody>
              {saleDetails.items.map((item) => {
                const itemCost = item.cost_price * item.quantity;
                const itemProfit = item.line_total - itemCost;
                const itemMargin = ((itemProfit / item.line_total) * 100).toFixed(1);

                return (
                  <tr key={item.id}>
                    <td>{item.product_name}</td>
                    <td>
                      <span className="presentation-badge">
                        {item.presentation_name}
                      </span>
                      {item.bulk_conversion_id && (
                        <span className="bulk-badge">🌾 Granel</span>
                      )}
                    </td>
                    <td className="text-center">{item.quantity}</td>
                    <td className="text-right">${item.cost_price.toFixed(2)}</td>
                    <td className="text-right">${item.unit_price.toFixed(2)}</td>
                    <td className="text-right font-bold">
                      ${item.line_total.toFixed(2)}
                    </td>
                    <td className="text-right">
                      <span className={itemProfit > 0 ? 'profit' : 'loss'}>
                        {itemMargin}%
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Resumen Financiero */}
        <div className="financial-summary">
          <div className="summary-row">
            <span className="label">Costo Total:</span>
            <span className="value cost">${totalCost.toFixed(2)}</span>
          </div>
          <div className="summary-row">
            <span className="label">Total Venta:</span>
            <span className="value total">${saleDetails.total.toFixed(2)}</span>
          </div>
          <div className="summary-row highlight">
            <span className="label">Ganancia:</span>
            <span className="value profit">
              ${totalProfit.toFixed(2)} ({profitMargin}%)
            </span>
          </div>
        </div>

        {/* Acciones */}
        <div className="modal-footer">
          <button className="btn-print" onClick={() => window.print()}>
            🖨️ Imprimir
          </button>
          <button className="btn-close" onClick={onClose}>
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};
```

---

### 4. **CSS para el Modal** (Ejemplo)

```css
/* styles/SaleDetailsModal.css */
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
  max-width: 900px;
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

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
}

.close-btn:hover {
  color: #ef4444;
}

.sale-info-section,
.customer-section,
.seller-section {
  margin-bottom: 20px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.info-row .label {
  font-weight: 600;
  color: #4b5563;
}

.badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge.completed {
  background: #d1fae5;
  color: #065f46;
}

.items-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
}

.items-table th,
.items-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.items-table th {
  background: #f3f4f6;
  font-weight: 600;
  color: #374151;
}

.text-center {
  text-align: center;
}

.text-right {
  text-align: right;
}

.font-bold {
  font-weight: 700;
}

.bulk-badge {
  display: inline-block;
  margin-left: 8px;
  padding: 2px 8px;
  background: #fef3c7;
  color: #92400e;
  font-size: 11px;
  border-radius: 4px;
}

.financial-summary {
  margin-top: 20px;
  padding: 16px;
  background: #f3f4f6;
  border-radius: 8px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 16px;
}

.summary-row.highlight {
  border-top: 2px solid #d1d5db;
  margin-top: 8px;
  padding-top: 16px;
  font-weight: 700;
  font-size: 18px;
}

.value.profit {
  color: #059669;
}

.value.cost {
  color: #dc2626;
}

.value.total {
  color: #2563eb;
  font-weight: 700;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 2px solid #e5e7eb;
}

.btn-print,
.btn-close {
  padding: 10px 20px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-print {
  background: #3b82f6;
  color: white;
}

.btn-print:hover {
  background: #2563eb;
}

.btn-close {
  background: #6b7280;
  color: white;
}

.btn-close:hover {
  background: #4b5563;
}
```

---

## 💡 Uso en el Historial de Ventas

### Integración con Tabla de Ventas

```typescript
// components/SalesHistoryTable.tsx
import React, { useState } from 'react';
import { SaleDetailsModal } from './SaleDetailsModal';

export const SalesHistoryTable: React.FC = () => {
  const [selectedSaleId, setSelectedSaleId] = useState<string | null>(null);

  const handleViewDetails = (saleId: string) => {
    setSelectedSaleId(saleId);
  };

  const handleCloseModal = () => {
    setSelectedSaleId(null);
  };

  return (
    <>
      <table className="sales-table">
        <thead>
          <tr>
            <th>Código</th>
            <th>Fecha</th>
            <th>Cliente</th>
            <th>Total</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {/* ... filas de ventas ... */}
          <tr>
            <td>VEN-20251012120530</td>
            <td>2025-10-12 12:05</td>
            <td>Juan Pérez</td>
            <td>$87.50</td>
            <td>
              <button 
                onClick={() => handleViewDetails('550e8400-e29b-41d4-a716-446655440000')}
                className="btn-details"
              >
                Ver Detalles
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      {/* Modal de Detalles */}
      {selectedSaleId && (
        <SaleDetailsModal 
          saleId={selectedSaleId}
          onClose={handleCloseModal}
        />
      )}
    </>
  );
};
```

---

## ⚠️ Manejo de Errores

### Códigos de Error HTTP

| Código | Descripción | Solución |
|--------|-------------|----------|
| **401** | No autorizado | Verificar que el token esté presente y sea válido |
| **404** | Venta no encontrada | Verificar que el `sale_id` sea correcto |
| **500** | Error interno del servidor | Contactar soporte o revisar logs del backend |

### Ejemplo de Manejo

```typescript
try {
  const details = await getSaleDetails(saleId, token);
  console.log('Detalles obtenidos:', details);
} catch (error) {
  if (axios.isAxiosError(error)) {
    switch (error.response?.status) {
      case 401:
        console.error('Token expirado o inválido');
        // Redirigir al login
        break;
      case 404:
        console.error('Venta no encontrada');
        // Mostrar mensaje al usuario
        break;
      default:
        console.error('Error desconocido:', error.message);
    }
  }
}
```

---

## 📊 Casos de Uso

### 1. **Ver Detalles desde Historial**
El usuario hace clic en "Ver Detalles" en el historial de ventas y se abre un modal con toda la información.

### 2. **Imprimir Factura Detallada**
Mostrar el modal con la información completa y usar `window.print()` para imprimir.

### 3. **Análisis de Rentabilidad**
Calcular márgenes de ganancia comparando `cost_price` con `unit_price`.

### 4. **Auditoría de Ventas**
Revisar qué productos fueron vendidos, de qué lotes, y por quién.

---

## ✅ Checklist de Implementación

- [ ] Crear servicio `getSaleDetails` en `salesService.ts`
- [ ] Crear hook `useSaleDetails` para manejo de estado
- [ ] Implementar componente `SaleDetailsModal`
- [ ] Agregar estilos CSS para el modal
- [ ] Integrar botón "Ver Detalles" en historial de ventas
- [ ] Agregar manejo de errores (401, 404, 500)
- [ ] Probar con diferentes tipos de ventas (empaquetadas y granel)
- [ ] Implementar cálculo de margen de ganancia
- [ ] Agregar funcionalidad de impresión
- [ ] Validar que los datos se muestran correctamente

---

## 🎯 Ventajas de Este Endpoint

✅ **Información Completa**: Toda la información de la venta en una sola llamada  
✅ **Nombres Legibles**: Muestra nombres de productos en lugar de solo IDs  
✅ **Precio de Costo**: Permite calcular rentabilidad de cada venta  
✅ **Datos del Cliente y Vendedor**: Contexto completo de la transacción  
✅ **Identificación de Tipo**: Distingue entre ventas empaquetadas y a granel  
✅ **Listo para Imprimir**: Formato ideal para facturas detalladas  

---

## 🔗 Endpoints Relacionados

- **GET `/sales/`** - Listado de ventas con paginación y filtros
- **POST `/sales/`** - Crear nueva venta
- **GET `/sales/{sale_id}/details`** - **Este endpoint** (detalles completos)

---

## 📞 Soporte

Si tienes dudas o encuentras algún problema:
1. Verifica que el backend esté corriendo
2. Confirma que el token de autenticación sea válido
3. Valida que el `sale_id` sea un UUID correcto
4. Revisa la consola del navegador para errores específicos

---

**¡Endpoint listo para usar! 🎉**
