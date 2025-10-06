# 🎯 Guía Rápida de Implementación Frontend

## 📋 Endpoints Esenciales

### 🔐 Autenticación
```javascript
// Login
POST /auth/login
{
  "email": "test@example.com",
  "password": "123456"
}

// Headers para requests autenticados
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
```

### 💰 Ventas (Endpoint Principal)
```javascript
// Crear venta
POST /sales/
{
  "customer_id": "uuid-del-cliente",
  "status": "completed",
  "items": [
    {
      "presentation_id": "uuid-de-presentacion",
      "quantity": 2,
      "unit_price": 15.50
    }
  ]
}

// Listar ventas
GET /sales/?skip=0&limit=50

// Detalle de venta
GET /sales/{sale_id}

// Productos más vendidos
GET /sales/reports/best-products?limit=10
```

### 📦 Inventario
```javascript
// Categorías
GET /inventory/categories

// Productos por categoría
GET /inventory/categories/{category_id}/products

// Stock disponible
GET /inventory/presentations/{presentation_id}/stock

// Crear lote
POST /inventory/lots
{
  "supplier_id": "uuid-proveedor",
  "received_date": "2024-10-05T10:00:00",
  "lot_code": "LOT-001",
  "status": "active"
}

// Agregar productos al lote
POST /inventory/lots/{lot_id}/products
{
  "presentation_id": "uuid-presentacion",
  "quantity_received": 100,
  "unit_cost": 1.50,
  "expiration_date": "2025-12-31T23:59:59"
}
```

---

## 🛠️ Clase JavaScript para Ventas

```javascript
class MAPOSalesAPI {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('token');
  }

  // Configurar headers
  getHeaders() {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.token}`
    };
  }

  // Login
  async login(email, password) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    if (response.ok) {
      const data = await response.json();
      this.token = data.access_token;
      localStorage.setItem('token', this.token);
      return data;
    }
    throw new Error('Login failed');
  }

  // Crear venta
  async createSale(customerId, items) {
    const saleData = {
      customer_id: customerId,
      status: "completed",
      items: items.map(item => ({
        presentation_id: item.presentationId,
        quantity: item.quantity,
        unit_price: item.unitPrice
      }))
    };

    const response = await fetch(`${this.baseURL}/sales/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(saleData)
    });

    if (response.ok) {
      return await response.json();
    }
    
    const error = await response.json();
    throw new Error(error.detail || 'Sale creation failed');
  }

  // Obtener productos por categoría
  async getProductsByCategory(categoryId) {
    const response = await fetch(
      `${this.baseURL}/inventory/categories/${categoryId}/products`,
      { headers: this.getHeaders() }
    );
    
    if (response.ok) {
      return await response.json();
    }
    throw new Error('Failed to fetch products');
  }

  // Verificar stock
  async checkStock(presentationId) {
    const response = await fetch(
      `${this.baseURL}/inventory/presentations/${presentationId}/stock`,
      { headers: this.getHeaders() }
    );
    
    if (response.ok) {
      return await response.json();
    }
    throw new Error('Failed to check stock');
  }

  // Obtener ventas
  async getSales(skip = 0, limit = 50) {
    const response = await fetch(
      `${this.baseURL}/sales/?skip=${skip}&limit=${limit}`,
      { headers: this.getHeaders() }
    );
    
    if (response.ok) {
      return await response.json();
    }
    throw new Error('Failed to fetch sales');
  }

  // Productos más vendidos
  async getBestSellingProducts(limit = 10) {
    const response = await fetch(
      `${this.baseURL}/sales/reports/best-products?limit=${limit}`,
      { headers: this.getHeaders() }
    );
    
    if (response.ok) {
      return await response.json();
    }
    throw new Error('Failed to fetch best selling products');
  }
}
```

---

## 🎨 Ejemplo de Uso (React/Vue/Vanilla JS)

### Inicialización
```javascript
const api = new MAPOSalesAPI();

// Login al iniciar la app
await api.login('test@example.com', '123456');
```

### Crear Venta
```javascript
// Definir items del carrito
const cartItems = [
  {
    presentationId: 'a83e3b1a-1038-4ec6-aea9-309592e1e41c',
    quantity: 2,
    unitPrice: 15.50
  },
  {
    presentationId: 'b94f4c2b-2149-5fd7-bfba-420683f2f52d',
    quantity: 1,
    unitPrice: 25.00
  }
];

// Procesar venta
try {
  const sale = await api.createSale(
    '67825f4c-e43f-4871-8b46-6016ceebbecf', // Customer ID
    cartItems
  );
  
  console.log('Venta creada:', sale.sale_code);
  console.log('Total:', sale.total);
} catch (error) {
  console.error('Error:', error.message);
}
```

### Verificar Stock Antes de Vender
```javascript
async function validateCartStock(cartItems) {
  for (const item of cartItems) {
    const stock = await api.checkStock(item.presentationId);
    
    if (stock.available_stock < item.quantity) {
      throw new Error(
        `Stock insuficiente. Disponible: ${stock.available_stock}, Solicitado: ${item.quantity}`
      );
    }
  }
  return true;
}
```

---

## 📊 Componentes UI Sugeridos

### 1. Cart Component (Carrito)
```html
<div id="sales-cart">
  <h3>Carrito de Ventas</h3>
  <div id="cart-items"></div>
  <div id="cart-total">Total: $0.00</div>
  <button onclick="processSale()">Procesar Venta</button>
</div>
```

### 2. Product Search (Búsqueda)
```html
<div id="product-search">
  <input type="text" id="search-input" placeholder="Buscar productos...">
  <select id="category-select">
    <option value="">Todas las categorías</option>
  </select>
  <div id="products-grid"></div>
</div>
```

### 3. Sales History (Historial)
```html
<div id="sales-history">
  <h3>Historial de Ventas</h3>
  <table id="sales-table">
    <thead>
      <tr>
        <th>Código</th>
        <th>Fecha</th>
        <th>Cliente</th>
        <th>Total</th>
        <th>Estado</th>
      </tr>
    </thead>
    <tbody></tbody>
  </table>
</div>
```

---

## 🚨 Manejo de Errores

```javascript
// Wrapper para manejo consistente de errores
async function safeAPICall(apiCall, errorMessage = 'Error en la operación') {
  try {
    return await apiCall();
  } catch (error) {
    // Log del error completo
    console.error('API Error:', error);
    
    // Mostrar mensaje amigable al usuario
    showNotification(errorMessage + ': ' + error.message, 'error');
    
    // Re-lanzar si es necesario para manejo específico
    throw error;
  }
}

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
  // Implementar según tu framework UI (toasts, alerts, etc.)
  console.log(`[${type.toUpperCase()}] ${message}`);
}
```

---

## 🔄 Estados de Loading

```javascript
class UIManager {
  static showLoading(elementId) {
    const element = document.getElementById(elementId);
    element.innerHTML = '<div class="loading">Cargando...</div>';
  }
  
  static hideLoading(elementId) {
    const element = document.getElementById(elementId);
    element.querySelector('.loading')?.remove();
  }
  
  static async withLoading(elementId, asyncOperation) {
    this.showLoading(elementId);
    try {
      const result = await asyncOperation();
      return result;
    } finally {
      this.hideLoading(elementId);
    }
  }
}

// Uso
await UIManager.withLoading('products-grid', async () => {
  return await api.getProductsByCategory(categoryId);
});
```

---

## ✅ Checklist de Implementación

### Básico (MVP)
- [ ] Login/logout
- [ ] Crear venta simple (1 producto)
- [ ] Ver lista de ventas
- [ ] Buscar productos

### Intermedio
- [ ] Carrito de ventas (múltiples productos)
- [ ] Validación de stock
- [ ] Gestión de clientes
- [ ] Reportes básicos

### Avanzado
- [ ] Gestión de inventario
- [ ] Reportes detallados
- [ ] Dashboard con métricas
- [ ] Impresión de comprobantes

---

## 🎯 URLs Importantes

- **API Base:** `http://localhost:8000`
- **Documentación:** `http://localhost:8000/docs`
- **Esquemas:** `http://localhost:8000/openapi.json`

---

## 🚀 ¡Comienza Aquí!

1. **Copia la clase `MAPOSalesAPI`** en tu proyecto
2. **Implementa el login** como primer paso
3. **Crea una venta simple** para validar la integración
4. **Construye el carrito** y la búsqueda de productos
5. **Agrega reportes** y funcionalidades avanzadas

¡El backend está listo y esperando! 🎉