# 📊 Historial de Ventas - Guía de Implementación Frontend

## 🎯 Descripción General

El endpoint de historial de ventas permite obtener todas las ventas registradas con:
- ✅ **Filtros opcionales por fecha** (inicio y fin)
- ✅ **Paginación** (skip y limit)
- ✅ **Ordenamiento automático** (más recientes primero)
- ✅ **Autenticación requerida**

---

## 🔗 Endpoint Principal

```http
GET /sales/
```

### **Query Parameters (todos opcionales)**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `skip` | integer | 0 | Número de registros a saltar (paginación) |
| `limit` | integer | 100 | Cantidad máxima de resultados (max: 1000) |
| `start_date` | datetime | null | Fecha de inicio (formato ISO 8601) |
| `end_date` | datetime | null | Fecha de fin (formato ISO 8601) |

---

## 📋 Ejemplos de Uso

### **1️⃣ Obtener Todas las Ventas (Últimas 100)**

```javascript
const response = await fetch('http://localhost:8000/sales/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  }
});

const sales = await response.json();
console.log('Últimas 100 ventas:', sales);
```

**Resultado esperado:**
```json
[
  {
    "id": "sale-uuid-1",
    "sale_code": "VEN-20251012143000",
    "customer_id": "customer-uuid",
    "user_id": "user-uuid",
    "sale_date": "2025-10-12T14:30:00",
    "total": 125000.00,
    "status": "completed",
    "sale_details": [...]
  },
  {
    "id": "sale-uuid-2",
    "sale_code": "VEN-20251012120000",
    "customer_id": "customer-uuid",
    "sale_date": "2025-10-12T12:00:00",
    "total": 85000.00,
    "status": "completed",
    "sale_details": [...]
  }
]
```

**Nota**: Las ventas vienen ordenadas de más reciente a más antigua.

---

### **2️⃣ Filtrar por Rango de Fechas**

```javascript
// Ventas de octubre 2025
const params = new URLSearchParams({
  start_date: '2025-10-01T00:00:00',
  end_date: '2025-10-31T23:59:59'
});

const response = await fetch(`http://localhost:8000/sales/?${params}`, {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  }
});

const salesOctober = await response.json();
```

---

### **3️⃣ Filtrar por Fecha Desde Hoy**

```javascript
// Ventas desde hoy en adelante
const today = new Date().toISOString();

const params = new URLSearchParams({
  start_date: today
});

const response = await fetch(`http://localhost:8000/sales/?${params}`, {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  }
});

const recentSales = await response.json();
```

---

### **4️⃣ Filtrar Ventas de la Última Semana**

```javascript
// Calcular fecha de hace 7 días
const today = new Date();
const lastWeek = new Date();
lastWeek.setDate(today.getDate() - 7);

const params = new URLSearchParams({
  start_date: lastWeek.toISOString(),
  end_date: today.toISOString()
});

const response = await fetch(`http://localhost:8000/sales/?${params}`, {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  }
});

const lastWeekSales = await response.json();
```

---

### **5️⃣ Paginación (Cargar Más Resultados)**

```javascript
// Primera página (primeras 50 ventas)
let skip = 0;
const limit = 50;

const response1 = await fetch(`http://localhost:8000/sales/?skip=${skip}&limit=${limit}`, {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  }
});

const page1 = await response1.json();

// Segunda página (siguientes 50 ventas)
skip = 50;

const response2 = await fetch(`http://localhost:8000/sales/?skip=${skip}&limit=${limit}`, {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  }
});

const page2 = await response2.json();
```

---

### **6️⃣ Combinar Filtros (Fecha + Paginación)**

```javascript
// Ventas de octubre, página 2
const params = new URLSearchParams({
  start_date: '2025-10-01T00:00:00',
  end_date: '2025-10-31T23:59:59',
  skip: 50,
  limit: 50
});

const response = await fetch(`http://localhost:8000/sales/?${params}`, {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  }
});

const salesPage2 = await response.json();
```

---

## 🎯 Hook Personalizado (React/TypeScript)

### **useSalesHistory.ts**

```typescript
import { useState } from 'react';

interface Sale {
  id: string;
  sale_code: string;
  customer_id: string;
  user_id: string;
  sale_date: string;
  total: number;
  status: string;
  sale_details: SaleDetail[];
}

interface SaleDetail {
  id: string;
  product_id: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

interface SalesFilters {
  skip?: number;
  limit?: number;
  start_date?: string;
  end_date?: string;
}

export function useSalesHistory() {
  const [sales, setSales] = useState<Sale[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);

  const fetchSales = async (filters: SalesFilters = {}) => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No hay sesión activa. Por favor inicia sesión.');
      }

      // Construir query params
      const params = new URLSearchParams();
      
      if (filters.skip !== undefined) params.append('skip', filters.skip.toString());
      if (filters.limit !== undefined) params.append('limit', filters.limit.toString());
      if (filters.start_date) params.append('start_date', filters.start_date);
      if (filters.end_date) params.append('end_date', filters.end_date);

      const url = `http://localhost:8000/sales/${params.toString() ? '?' + params.toString() : ''}`;

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al obtener ventas');
      }

      const data = await response.json();
      
      // Si recibimos menos resultados que el límite, no hay más datos
      const limit = filters.limit || 100;
      setHasMore(data.length === limit);
      
      setSales(data);
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const loadMoreSales = async (currentSales: Sale[], limit: number = 50) => {
    const moreSales = await fetchSales({ skip: currentSales.length, limit });
    setSales([...currentSales, ...moreSales]);
    return moreSales;
  };

  const filterByDateRange = async (startDate: Date, endDate: Date) => {
    return fetchSales({
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString()
    });
  };

  const filterByLastDays = async (days: number) => {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - days);

    return fetchSales({
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString()
    });
  };

  return {
    sales,
    loading,
    error,
    hasMore,
    fetchSales,
    loadMoreSales,
    filterByDateRange,
    filterByLastDays
  };
}
```

---

## 💻 Componente React Completo

### **SalesHistory.tsx**

```tsx
import React, { useEffect, useState } from 'react';
import { useSalesHistory } from '../hooks/useSalesHistory';

export function SalesHistory() {
  const { sales, loading, error, hasMore, fetchSales, loadMoreSales, filterByLastDays } = useSalesHistory();
  const [filter, setFilter] = useState<'all' | 'today' | 'week' | 'month'>('all');

  useEffect(() => {
    // Cargar ventas al montar el componente
    fetchSales();
  }, []);

  const handleFilterChange = async (newFilter: typeof filter) => {
    setFilter(newFilter);

    switch (newFilter) {
      case 'all':
        await fetchSales();
        break;
      case 'today':
        await filterByLastDays(1);
        break;
      case 'week':
        await filterByLastDays(7);
        break;
      case 'month':
        await filterByLastDays(30);
        break;
    }
  };

  const handleLoadMore = async () => {
    await loadMoreSales(sales);
  };

  if (loading && sales.length === 0) {
    return <div className="loading">Cargando historial de ventas...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="sales-history">
      <h2>Historial de Ventas</h2>

      {/* Filtros */}
      <div className="filters">
        <button 
          onClick={() => handleFilterChange('all')}
          className={filter === 'all' ? 'active' : ''}
        >
          Todas
        </button>
        <button 
          onClick={() => handleFilterChange('today')}
          className={filter === 'today' ? 'active' : ''}
        >
          Hoy
        </button>
        <button 
          onClick={() => handleFilterChange('week')}
          className={filter === 'week' ? 'active' : ''}
        >
          Última Semana
        </button>
        <button 
          onClick={() => handleFilterChange('month')}
          className={filter === 'month' ? 'active' : ''}
        >
          Último Mes
        </button>
      </div>

      {/* Tabla de Ventas */}
      <table className="sales-table">
        <thead>
          <tr>
            <th>Código</th>
            <th>Fecha</th>
            <th>Cliente</th>
            <th>Total</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {sales.map((sale) => (
            <tr key={sale.id}>
              <td>{sale.sale_code}</td>
              <td>{new Date(sale.sale_date).toLocaleString()}</td>
              <td>{sale.customer_id}</td>
              <td>${sale.total.toFixed(2)}</td>
              <td>
                <span className={`status ${sale.status}`}>
                  {sale.status === 'completed' ? 'Completada' : sale.status}
                </span>
              </td>
              <td>
                <button onClick={() => console.log('Ver detalles:', sale.id)}>
                  Ver Detalles
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Botón Cargar Más */}
      {hasMore && (
        <button 
          onClick={handleLoadMore} 
          disabled={loading}
          className="load-more"
        >
          {loading ? 'Cargando...' : 'Cargar Más'}
        </button>
      )}

      {/* Resumen */}
      <div className="summary">
        <p>Mostrando {sales.length} ventas</p>
        <p>Total: ${sales.reduce((sum, sale) => sum + sale.total, 0).toFixed(2)}</p>
      </div>
    </div>
  );
}
```

---

## 🎨 Componente con Selector de Fechas Personalizado

### **SalesHistoryWithDatePicker.tsx**

```tsx
import React, { useState } from 'react';
import { useSalesHistory } from '../hooks/useSalesHistory';

export function SalesHistoryWithDatePicker() {
  const { sales, loading, error, filterByDateRange } = useSalesHistory();
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const handleFilterByDate = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!startDate || !endDate) {
      alert('Por favor selecciona ambas fechas');
      return;
    }

    const start = new Date(startDate);
    const end = new Date(endDate);

    if (start > end) {
      alert('La fecha de inicio debe ser anterior a la fecha de fin');
      return;
    }

    await filterByDateRange(start, end);
  };

  const handleClearFilters = async () => {
    setStartDate('');
    setEndDate('');
    await useSalesHistory().fetchSales();
  };

  return (
    <div className="sales-history-with-datepicker">
      <h2>Historial de Ventas</h2>

      {/* Filtro de Fechas */}
      <form onSubmit={handleFilterByDate} className="date-filter">
        <div>
          <label htmlFor="start-date">Fecha Inicio:</label>
          <input
            type="datetime-local"
            id="start-date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </div>

        <div>
          <label htmlFor="end-date">Fecha Fin:</label>
          <input
            type="datetime-local"
            id="end-date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Filtrando...' : 'Filtrar'}
        </button>

        <button type="button" onClick={handleClearFilters}>
          Limpiar Filtros
        </button>
      </form>

      {/* Resultados */}
      {error && <div className="error">{error}</div>}

      {loading && <div className="loading">Cargando...</div>}

      {!loading && sales.length === 0 && (
        <div className="no-results">
          No se encontraron ventas para el rango de fechas seleccionado.
        </div>
      )}

      {!loading && sales.length > 0 && (
        <div className="results">
          <p>Se encontraron {sales.length} ventas</p>
          
          <table>
            <thead>
              <tr>
                <th>Código</th>
                <th>Fecha</th>
                <th>Total</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {sales.map((sale) => (
                <tr key={sale.id}>
                  <td>{sale.sale_code}</td>
                  <td>{new Date(sale.sale_date).toLocaleString()}</td>
                  <td>${sale.total.toFixed(2)}</td>
                  <td>{sale.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
```

---

## 📱 Servicio JavaScript Puro (sin React)

### **salesHistoryService.js**

```javascript
class SalesHistoryService {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }

  async getAllSales(filters = {}) {
    const { skip = 0, limit = 100, start_date, end_date } = filters;
    
    const params = new URLSearchParams();
    params.append('skip', skip);
    params.append('limit', limit);
    if (start_date) params.append('start_date', start_date);
    if (end_date) params.append('end_date', end_date);

    const response = await fetch(
      `${this.baseURL}/sales/?${params}`,
      { headers: this.getAuthHeaders() }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al obtener ventas');
    }

    return await response.json();
  }

  async getSalesToday() {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    return this.getAllSales({
      start_date: today.toISOString(),
      end_date: tomorrow.toISOString()
    });
  }

  async getSalesLastWeek() {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - 7);

    return this.getAllSales({
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString()
    });
  }

  async getSalesLastMonth() {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setMonth(endDate.getMonth() - 1);

    return this.getAllSales({
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString()
    });
  }

  async getSalesByDateRange(startDate, endDate) {
    return this.getAllSales({
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString()
    });
  }
}

export const salesHistoryService = new SalesHistoryService();
```

---

## 🔧 Ejemplos con Fetch Directo

### **Ejemplo 1: Ventas de Hoy**

```javascript
async function getSalesToday() {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  const params = new URLSearchParams({
    start_date: today.toISOString(),
    end_date: tomorrow.toISOString()
  });

  const response = await fetch(`http://localhost:8000/sales/?${params}`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    }
  });

  const salesToday = await response.json();
  console.log('Ventas de hoy:', salesToday);
  return salesToday;
}
```

---

### **Ejemplo 2: Ventas del Mes Actual**

```javascript
async function getSalesThisMonth() {
  const now = new Date();
  const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
  const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59);

  const params = new URLSearchParams({
    start_date: firstDay.toISOString(),
    end_date: lastDay.toISOString()
  });

  const response = await fetch(`http://localhost:8000/sales/?${params}`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    }
  });

  return await response.json();
}
```

---

### **Ejemplo 3: Últimas 10 Ventas**

```javascript
async function getLastTenSales() {
  const params = new URLSearchParams({
    limit: '10'
  });

  const response = await fetch(`http://localhost:8000/sales/?${params}`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    }
  });

  return await response.json();
}
```

---

## 🎯 Ejemplos con Axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para agregar token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Obtener todas las ventas
export const getAllSales = async (filters = {}) => {
  const response = await api.get('/sales/', { params: filters });
  return response.data;
};

// Ventas de hoy
export const getSalesToday = async () => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  return getAllSales({
    start_date: today.toISOString(),
    end_date: tomorrow.toISOString()
  });
};

// Ventas por rango de fechas
export const getSalesByDateRange = async (startDate, endDate) => {
  return getAllSales({
    start_date: startDate,
    end_date: endDate
  });
};
```

---

## 📊 Formato de Respuesta

```json
[
  {
    "id": "uuid-venta-1",
    "sale_code": "VEN-20251012143000",
    "customer_id": "uuid-cliente",
    "user_id": "uuid-usuario",
    "sale_date": "2025-10-12T14:30:00",
    "total": 125000.00,
    "status": "completed",
    "items": [
      {
        "id": "uuid-detalle-1",
        "sale_id": "uuid-venta-1",
        "presentation_id": "uuid-presentacion",
        "lot_detail_id": "uuid-lote",
        "bulk_conversion_id": null,
        "quantity": 10,
        "unit_price": 2500.00,
        "line_total": 25000.00
      },
      {
        "id": "uuid-detalle-2",
        "sale_id": "uuid-venta-1",
        "presentation_id": "uuid-presentacion",
        "lot_detail_id": null,
        "bulk_conversion_id": "uuid-conversion",
        "quantity": 40,
        "unit_price": 2500.00,
        "line_total": 100000.00
      }
    ]
  }
]
```

**Nota**: Cada venta incluye automáticamente su array de `items` con todos los detalles de la venta.

---

## ⚠️ Errores Comunes

### **Error 401: Unauthorized**

```json
{
  "detail": "Authentication required"
}
```

**Solución**: Asegúrate de incluir el token en el header `Authorization`.

---

### **Error 422: Validation Error**

```json
{
  "detail": [
    {
      "loc": ["query", "start_date"],
      "msg": "invalid datetime format",
      "type": "value_error"
    }
  ]
}
```

**Solución**: Usa formato ISO 8601 para las fechas: `2025-10-12T14:30:00`

---

## 📋 Checklist de Implementación

- [ ] ✅ Incluir header `Authorization: Bearer ${token}` en todas las peticiones
- [ ] ✅ Usar formato ISO 8601 para fechas: `new Date().toISOString()`
- [ ] ✅ Las ventas vienen ordenadas de más reciente a más antigua automáticamente
- [ ] ✅ Implementar paginación con `skip` y `limit`
- [ ] ✅ Manejar casos cuando no hay resultados
- [ ] ✅ Mostrar loading mientras se cargan las ventas
- [ ] ✅ Manejar errores de autenticación (401)
- [ ] ✅ Validar que `start_date` <= `end_date` en el frontend

---

## 💡 Tips Adicionales

### **Optimización de Rendimiento**

```javascript
// Cargar solo las últimas 20 ventas inicialmente
const initialSales = await fetchSales({ limit: 20 });

// Cargar más cuando el usuario haga scroll o click en "Cargar más"
const moreSales = await fetchSales({ skip: 20, limit: 20 });
```

---

### **Formateo de Fechas**

```javascript
// Formatear fecha para mostrar
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleString('es-CO', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// Uso
console.log(formatDate('2025-10-12T14:30:00')); 
// "12 de octubre de 2025, 14:30"
```

---

### **Calcular Totales**

```javascript
// Calcular total de ventas
const totalAmount = sales.reduce((sum, sale) => sum + sale.total, 0);

// Calcular promedio
const averageAmount = totalAmount / sales.length;

// Contar ventas por estado
const completedSales = sales.filter(s => s.status === 'completed').length;
```

---

## 🎉 Resumen

- **Endpoint**: `GET /sales/`
- **Filtros opcionales**: `start_date`, `end_date`, `skip`, `limit`
- **Ordenamiento**: Automático (más recientes primero)
- **Autenticación**: Requerida (`Bearer token`)
- **Formato de fechas**: ISO 8601 (`2025-10-12T14:30:00`)

---

📚 **Documentación Relacionada:**
- [SWAGGER_EXAMPLES.md](./SWAGGER_EXAMPLES.md) - Ejemplos para testing
- [FIX_AUTH_ERROR_401.md](./FIX_AUTH_ERROR_401.md) - Solución a errores de autenticación
- [SALES_SYSTEM_COMPLETE_GUIDE.md](./SALES_SYSTEM_COMPLETE_GUIDE.md) - Guía completa del sistema
