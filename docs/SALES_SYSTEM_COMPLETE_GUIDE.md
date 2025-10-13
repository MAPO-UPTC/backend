# 🛒 Sistema de Ventas - Guía Completa de Implementación Frontend

## 📋 Índice
1. [Información General](#información-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Endpoints Disponibles](#endpoints-disponibles)
4. [Flujo de Trabajo de Ventas](#flujo-de-trabajo-de-ventas)
5. [Implementación Frontend](#implementación-frontend)
6. [Ejemplos de Código](#ejemplos-de-código)
7. [Manejo de Errores](#manejo-de-errores)

---

## 📊 Información General

El sistema de ventas maneja dos tipos de productos:
- **Productos Empaquetados**: Productos en su presentación original (lotes completos)
- **Productos a Granel**: Productos divididos de presentaciones grandes (ej: 25kg → venta por kg)

### ✨ **CARACTERÍSTICA IMPORTANTE: Ventas Mixtas Automáticas**

El sistema soporta **ventas mixtas en una sola transacción**. Esto significa que puedes vender:
- ✅ Solo productos empaquetados
- ✅ Solo productos a granel  
- ✅ **AMBOS en la misma venta** (¡automático!)

**Estrategia de Venta Automática:**
1. El sistema primero intenta vender de stock empaquetado (FIFO - First In, First Out)
2. Si no hay suficiente stock empaquetado, **automáticamente usa stock a granel**
3. Puede combinar ambos en la misma venta sin que el frontend deba especificarlo

**Ejemplo:** Si pides 10 unidades de "Arroz Diana 1kg" y solo hay 7 empaquetadas + 5kg a granel disponibles, el sistema:
- Vende las 7 unidades empaquetadas
- Vende 3kg del stock a granel
- **Total: 10 unidades vendidas en una sola transacción** ✅

### **Conceptos Clave**

| Concepto | Descripción | Ejemplo |
|----------|-------------|---------|
| `presentation_id` | ID de la presentación del producto | Arroz Diana 25kg, Arroz Diana 1kg |
| `lot_detail_id` | ID del lote específico (para empaquetados) | Lote de 100 unidades de Arroz 1kg |
| `bulk_conversion_id` | ID de la conversión a granel | 25kg convertidos a venta por kg |
| `quantity` | Cantidad a vender | 5 (unidades para empaquetado, kg/g para granel) |
| `unit_price` | Precio por unidad | 3500 por kg, 45000 por unidad |

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                     FLUJO DE VENTA                          │
└─────────────────────────────────────────────────────────────┘

1. Seleccionar Cliente (GET /api/v1/persons/)
   ↓
2. Cargar Productos Disponibles (GET /api/v1/products/)
   ├─ Productos con stock empaquetado (current_stock > 0)
   └─ Productos con stock a granel (bulk_stock_available > 0)
   ↓
3. Agregar Items al Carrito
   ├─ Validar stock disponible
   ├─ Calcular subtotales
   └─ Calcular total
   ↓
4. Confirmar Venta (POST /api/v1/sales/)
   ├─ Enviar todos los items
   ├─ Backend valida stock
   ├─ Backend descuenta inventario
   └─ Backend genera código de venta
   ↓
5. Recibir Confirmación
   └─ Mostrar código de venta, total, detalles
```

---

## 🔗 Endpoints Disponibles

### **1. Obtener Productos Disponibles**

```http
GET /api/v1/products/
```

**Headers:**
```http
Authorization: Bearer {token}
Content-Type: application/json
```

**Respuesta:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Arroz Diana",
    "category_name": "Granos",
    "presentations": [
      {
        "id": "650e8400-e29b-41d4-a716-446655440001",
        "name": "Arroz Diana 1kg",
        "unit_of_measure": "kg",
        "quantity": 1.0,
        "current_stock": 45,
        "bulk_stock_available": 0,
        "base_price": 4500.0,
        "is_bulk_source": false,
        "can_sell_bulk": false
      },
      {
        "id": "650e8400-e29b-41d4-a716-446655440002",
        "name": "Arroz Diana 25kg",
        "unit_of_measure": "kg",
        "quantity": 25.0,
        "current_stock": 10,
        "bulk_stock_available": 75.5,
        "base_price": 95000.0,
        "is_bulk_source": true,
        "can_sell_bulk": true
      }
    ]
  }
]
```

**Campos Importantes:**
- `current_stock`: Stock de productos empaquetados disponibles para venta
- `bulk_stock_available`: Stock en kg/g disponible para venta a granel
- `is_bulk_source`: Indica si esta presentación puede dividirse
- `can_sell_bulk`: Indica si se puede vender a granel

---

### **2. Crear Venta**

```http
POST /api/v1/sales/
```

**Headers:**
```http
Authorization: Bearer {token}
Content-Type: application/json
```

**Body:**
```json
{
  "customer_id": "customer-uuid-here",
  "status": "completed",
  "items": [
    {
      "presentation_id": "presentation-uuid-1",
      "quantity": 3,
      "unit_price": 4500.0
    },
    {
      "presentation_id": "presentation-uuid-2",
      "quantity": 5.5,
      "unit_price": 3800.0
    }
  ]
}
```

**Respuesta Exitosa (200):**
```json
{
  "id": "sale-uuid-here",
  "sale_code": "VTA-20251012-0001",
  "sale_date": "2025-10-12T10:30:00",
  "customer_id": "customer-uuid-here",
  "user_id": "user-uuid-here",
  "total": 34400.0,
  "status": "completed",
  "items": [
    {
      "id": "detail-uuid-1",
      "sale_id": "sale-uuid-here",
      "presentation_id": "presentation-uuid-1",
      "lot_detail_id": "lot-uuid-here",
      "bulk_conversion_id": null,
      "quantity": 3,
      "unit_price": 4500.0,
      "line_total": 13500.0
    },
    {
      "id": "detail-uuid-2",
      "sale_id": "sale-uuid-here",
      "presentation_id": "presentation-uuid-2",
      "lot_detail_id": null,
      "bulk_conversion_id": "bulk-uuid-here",
      "quantity": 5.5,
      "unit_price": 3800.0,
      "line_total": 20900.0
    }
  ]
}
```

**⚠️ IMPORTANTE - Interpretación de Respuesta:**

La respuesta puede contener **múltiples `items` (SaleDetails)** para un mismo producto si se vendió de diferentes fuentes:

```json
{
  "items": [
    // Mismo presentation_id, diferente origen
    {
      "presentation_id": "arroz-1kg-uuid",
      "lot_detail_id": "lot-A",
      "bulk_conversion_id": null,
      "quantity": 8  // 8 unidades de lote empaquetado
    },
    {
      "presentation_id": "arroz-1kg-uuid",
      "lot_detail_id": null,
      "bulk_conversion_id": "bulk-X",
      "quantity": 3  // 3kg de stock a granel
    }
    // TOTAL para este producto: 11 unidades (8 empaquetadas + 3 granel)
  ]
}
```

**Cómo Identificar el Origen:**
- Si `lot_detail_id != null` → Vendido de **stock empaquetado**
- Si `bulk_conversion_id != null` → Vendido de **stock a granel**
- Si necesitas agrupar por producto en el frontend, suma las cantidades del mismo `presentation_id`

---

### **3. Obtener Ventas**

```http
GET /api/v1/sales/?skip=0&limit=100
```

**Parámetros de Query:**
- `skip`: Número de registros a saltar (paginación)
- `limit`: Número máximo de registros a retornar

**Respuesta:**
```json
[
  {
    "id": "sale-uuid",
    "sale_code": "VTA-20251012-0001",
    "sale_date": "2025-10-12T10:30:00",
    "customer_id": "customer-uuid",
    "user_id": "user-uuid",
    "total": 34400.0,
    "status": "completed",
    "items": []
  }
]
```

---

### **4. Obtener Venta por ID**

```http
GET /api/v1/sales/{sale_id}
```

**Respuesta:** (Igual que la respuesta de crear venta)

---

### **5. Obtener Venta por Código**

```http
GET /api/v1/sales/code/{sale_code}
```

**Ejemplo:**
```http
GET /api/v1/sales/code/VTA-20251012-0001
```

---

### **6. Reporte de Ventas**

```http
GET /api/v1/sales/reports/summary?start_date=2025-10-01T00:00:00&end_date=2025-10-31T23:59:59
```

**Parámetros Opcionales:**
- `start_date`: Fecha inicial (ISO 8601)
- `end_date`: Fecha final (ISO 8601)
- `customer_id`: Filtrar por cliente
- `user_id`: Filtrar por usuario

**Respuesta:**
```json
{
  "sales": [
    {
      "sale_id": "uuid",
      "sale_code": "VTA-20251012-0001",
      "sale_date": "2025-10-12T10:30:00",
      "customer_id": "uuid",
      "user_id": "uuid",
      "total": 34400.0,
      "status": "completed"
    }
  ],
  "total_sales": 25,
  "total_revenue": 1250000.0,
  "period_start": "2025-10-01T00:00:00",
  "period_end": "2025-10-31T23:59:59"
}
```

---

### **7. Productos Más Vendidos**

```http
GET /api/v1/sales/reports/best-products?limit=10
```

**Respuesta:**
```json
{
  "best_selling_products": [
    {
      "presentation_id": "uuid",
      "presentation_name": "Arroz Diana 1kg",
      "total_sold": 150,
      "total_revenue": 675000.0
    }
  ],
  "generated_at": "2025-10-12T14:30:00"
}
```

---

### **8. Resumen Diario**

```http
GET /api/v1/sales/reports/daily/2025-10-12T00:00:00
```

**Respuesta:**
```json
{
  "date": "2025-10-12T00:00:00",
  "total_sales": 15,
  "total_revenue": 450000.0,
  "total_items_sold": 75,
  "average_sale_value": 30000.0
}
```

---

## 🔄 Flujo de Trabajo de Ventas

### **Paso 1: Cargar Clientes**

```javascript
// Obtener lista de clientes
const loadCustomers = async () => {
  const response = await fetch('/api/v1/persons/', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  const customers = await response.json();
  return customers;
};
```

### **Paso 2: Cargar Productos**

```javascript
// Obtener productos con stock
const loadProducts = async () => {
  const response = await fetch('/api/v1/products/', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  const products = await response.json();
  
  // Filtrar solo presentaciones con stock
  return products.map(product => ({
    ...product,
    presentations: product.presentations.filter(pres => 
      pres.current_stock > 0 || pres.bulk_stock_available > 0
    )
  })).filter(product => product.presentations.length > 0);
};
```

### **3. Gestionar Carrito de Compras**

```javascript
// Estado del carrito
const [cart, setCart] = useState([]);
const [customer, setCustomer] = useState(null);

// Agregar item al carrito
const addToCart = (presentation, quantity, isBulk = false) => {
  // Validar stock TOTAL (empaquetado + granel)
  const totalStock = presentation.current_stock + presentation.bulk_stock_available;
  
  if (quantity > totalStock) {
    alert(
      `Stock insuficiente.\n` +
      `Disponible: ${totalStock} (Empaquetado: ${presentation.current_stock}, Granel: ${presentation.bulk_stock_available})`
    );
    return;
  }
  
  // Calcular precio
  const unitPrice = presentation.base_price;
  const lineTotal = quantity * unitPrice;
  
  // Agregar al carrito
  const newItem = {
    presentation_id: presentation.id,
    presentation_name: presentation.name,
    quantity: quantity,
    unit_price: unitPrice,
    line_total: lineTotal,
    max_stock: totalStock
  };
  
  setCart([...cart, newItem]);
};

// Calcular total
const calculateTotal = () => {
  return cart.reduce((sum, item) => sum + item.line_total, 0);
};

// 🆕 AGRUPAR ITEMS DE VENTA MIXTA EN RESPUESTA
const groupSaleItems = (saleResponse) => {
  const grouped = {};
  
  saleResponse.items.forEach(item => {
    const key = item.presentation_id;
    
    if (!grouped[key]) {
      grouped[key] = {
        presentation_id: item.presentation_id,
        total_quantity: 0,
        total_line_total: 0,
        unit_price: item.unit_price,
        sources: []
      };
    }
    
    grouped[key].total_quantity += item.quantity;
    grouped[key].total_line_total += item.line_total;
    
    // Identificar origen
    const source = item.lot_detail_id 
      ? `Empaquetado (${item.quantity} un)` 
      : `Granel (${item.quantity} kg)`;
    
    grouped[key].sources.push(source);
  });
  
  return Object.values(grouped);
};

// Uso después de crear venta
const result = await processSale();
const groupedItems = groupSaleItems(result);

console.log('Items agrupados:', groupedItems);
// Ejemplo de salida:
// [
//   {
//     presentation_id: "arroz-uuid",
//     total_quantity: 11,
//     total_line_total: 49500,
//     unit_price: 4500,
//     sources: ["Empaquetado (8 un)", "Granel (3 kg)"]
//   }
// ]
```

### **Paso 4: Procesar Venta**

```javascript
const processSale = async () => {
  if (!customer) {
    alert('Debe seleccionar un cliente');
    return;
  }
  
  if (cart.length === 0) {
    alert('El carrito está vacío');
    return;
  }
  
  // Preparar datos de venta
  const saleData = {
    customer_id: customer.id,
    status: "completed",
    items: cart.map(item => ({
      presentation_id: item.presentation_id,
      quantity: item.quantity,
      unit_price: item.unit_price
    }))
  };
  
  try {
    const response = await fetch('/api/v1/sales/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(saleData)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al procesar venta');
    }
    
    const result = await response.json();
    
    // Mostrar confirmación
    alert(`Venta exitosa!\nCódigo: ${result.sale_code}\nTotal: $${result.total.toLocaleString()}`);
    
    // Limpiar carrito
    setCart([]);
    setCustomer(null);
    
    // Recargar productos para actualizar stock
    await loadProducts();
    
    return result;
    
  } catch (error) {
    console.error('Error:', error);
    alert(error.message);
  }
};
```

---

## 💻 Implementación Frontend

### **Componente Principal de Ventas**

```jsx
import React, { useState, useEffect } from 'react';

const SalesModule = () => {
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const token = localStorage.getItem('token'); // O tu método de auth
  
  useEffect(() => {
    loadInitialData();
  }, []);
  
  const loadInitialData = async () => {
    setLoading(true);
    try {
      const [customersData, productsData] = await Promise.all([
        loadCustomers(),
        loadProducts()
      ]);
      setCustomers(customersData);
      setProducts(productsData);
    } catch (error) {
      console.error('Error cargando datos:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const loadCustomers = async () => {
    const response = await fetch('/api/v1/persons/', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  };
  
  const loadProducts = async () => {
    const response = await fetch('/api/v1/products/', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    const data = await response.json();
    
    // Filtrar solo productos con stock
    return data.map(product => ({
      ...product,
      presentations: product.presentations.filter(pres => 
        pres.current_stock > 0 || pres.bulk_stock_available > 0
      )
    })).filter(product => product.presentations.length > 0);
  };
  
  const addToCart = (presentation, quantity, isBulk) => {
    const availableStock = isBulk 
      ? presentation.bulk_stock_available 
      : presentation.current_stock;
    
    if (quantity <= 0) {
      alert('La cantidad debe ser mayor a 0');
      return;
    }
    
    if (quantity > availableStock) {
      alert(`Stock insuficiente. Disponible: ${availableStock}`);
      return;
    }
    
    const newItem = {
      id: Date.now(), // ID temporal para el carrito
      presentation_id: presentation.id,
      presentation_name: presentation.name,
      quantity: parseFloat(quantity),
      unit_price: presentation.base_price,
      line_total: parseFloat(quantity) * presentation.base_price,
      is_bulk: isBulk,
      max_stock: availableStock
    };
    
    setCart([...cart, newItem]);
  };
  
  const removeFromCart = (itemId) => {
    setCart(cart.filter(item => item.id !== itemId));
  };
  
  const calculateTotal = () => {
    return cart.reduce((sum, item) => sum + item.line_total, 0);
  };
  
  const processSale = async () => {
    if (!selectedCustomer) {
      alert('Debe seleccionar un cliente');
      return;
    }
    
    if (cart.length === 0) {
      alert('El carrito está vacío');
      return;
    }
    
    setLoading(true);
    
    const saleData = {
      customer_id: selectedCustomer.id,
      status: "completed",
      items: cart.map(item => ({
        presentation_id: item.presentation_id,
        quantity: item.quantity,
        unit_price: item.unit_price
      }))
    };
    
    try {
      const response = await fetch('/api/v1/sales/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(saleData)
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Error al procesar venta');
      }
      
      const result = await response.json();
      
      alert(
        `✅ Venta Exitosa!\n\n` +
        `Código: ${result.sale_code}\n` +
        `Total: $${result.total.toLocaleString('es-CO')}\n` +
        `Fecha: ${new Date(result.sale_date).toLocaleString('es-CO')}`
      );
      
      // Limpiar y recargar
      setCart([]);
      setSelectedCustomer(null);
      await loadProducts();
      
    } catch (error) {
      console.error('Error:', error);
      alert(`❌ Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return <div className="loading">Cargando...</div>;
  }
  
  return (
    <div className="sales-module">
      <h1>🛒 Sistema de Ventas</h1>
      
      {/* Selector de Cliente */}
      <div className="customer-section">
        <h2>Cliente</h2>
        <select
          value={selectedCustomer?.id || ''}
          onChange={(e) => {
            const customer = customers.find(c => c.id === e.target.value);
            setSelectedCustomer(customer);
          }}
        >
          <option value="">Seleccionar cliente...</option>
          {customers.map(customer => (
            <option key={customer.id} value={customer.id}>
              {customer.full_name} - {customer.document_number}
            </option>
          ))}
        </select>
      </div>
      
      {/* Lista de Productos */}
      <div className="products-section">
        <h2>Productos Disponibles</h2>
        {products.map(product => (
          <ProductCard
            key={product.id}
            product={product}
            onAddToCart={addToCart}
          />
        ))}
      </div>
      
      {/* Carrito */}
      <div className="cart-section">
        <h2>Carrito ({cart.length} items)</h2>
        {cart.map(item => (
          <CartItem
            key={item.id}
            item={item}
            onRemove={removeFromCart}
          />
        ))}
        
        <div className="cart-total">
          <strong>Total: ${calculateTotal().toLocaleString('es-CO')}</strong>
        </div>
        
        <button
          onClick={processSale}
          disabled={!selectedCustomer || cart.length === 0 || loading}
          className="btn-process-sale"
        >
          {loading ? 'Procesando...' : 'Procesar Venta'}
        </button>
      </div>
    </div>
  );
};

export default SalesModule;
```

---

### **Componente de Tarjeta de Producto**

```jsx
const ProductCard = ({ product, onAddToCart }) => {
  const [selectedPresentation, setSelectedPresentation] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [saleType, setSaleType] = useState('packaged'); // 'packaged' o 'bulk'
  
  const handleAdd = () => {
    if (!selectedPresentation) {
      alert('Seleccione una presentación');
      return;
    }
    
    const isBulk = saleType === 'bulk';
    onAddToCart(selectedPresentation, quantity, isBulk);
    
    // Reset
    setQuantity(1);
  };
  
  return (
    <div className="product-card">
      <h3>{product.name}</h3>
      <p className="category">{product.category_name}</p>
      
      {/* Selector de Presentación */}
      <select
        value={selectedPresentation?.id || ''}
        onChange={(e) => {
          const pres = product.presentations.find(p => p.id === e.target.value);
          setSelectedPresentation(pres);
          setSaleType(pres?.can_sell_bulk ? 'bulk' : 'packaged');
        }}
      >
        <option value="">Seleccionar presentación...</option>
        {product.presentations.map(pres => (
          <option key={pres.id} value={pres.id}>
            {pres.name} - ${pres.base_price.toLocaleString()}
          </option>
        ))}
      </select>
      
      {selectedPresentation && (
        <div className="presentation-details">
          {/* Stock Empaquetado */}
          {selectedPresentation.current_stock > 0 && (
            <div className="stock-info">
              <input
                type="radio"
                id={`packaged-${selectedPresentation.id}`}
                name={`type-${selectedPresentation.id}`}
                value="packaged"
                checked={saleType === 'packaged'}
                onChange={() => setSaleType('packaged')}
              />
              <label htmlFor={`packaged-${selectedPresentation.id}`}>
                Empaquetado - Stock: {selectedPresentation.current_stock} unidades
              </label>
            </div>
          )}
          
          {/* Stock a Granel */}
          {selectedPresentation.can_sell_bulk && selectedPresentation.bulk_stock_available > 0 && (
            <div className="stock-info">
              <input
                type="radio"
                id={`bulk-${selectedPresentation.id}`}
                name={`type-${selectedPresentation.id}`}
                value="bulk"
                checked={saleType === 'bulk'}
                onChange={() => setSaleType('bulk')}
              />
              <label htmlFor={`bulk-${selectedPresentation.id}`}>
                A Granel - Disponible: {selectedPresentation.bulk_stock_available} {selectedPresentation.unit_of_measure}
              </label>
            </div>
          )}
          
          {/* Cantidad */}
          <div className="quantity-input">
            <label>
              Cantidad:
              <input
                type="number"
                min="0.1"
                step={saleType === 'bulk' ? '0.1' : '1'}
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
              />
              {saleType === 'bulk' && <span>{selectedPresentation.unit_of_measure}</span>}
            </label>
          </div>
          
          <button onClick={handleAdd} className="btn-add">
            Agregar al Carrito
          </button>
        </div>
      )}
    </div>
  );
};
```

---

### **Componente de Item del Carrito**

```jsx
const CartItem = ({ item, onRemove }) => {
  return (
    <div className="cart-item">
      <div className="item-info">
        <h4>{item.presentation_name}</h4>
        <p>{item.is_bulk ? '(A Granel)' : '(Empaquetado)'}</p>
      </div>
      
      <div className="item-details">
        <span>Cantidad: {item.quantity} {item.is_bulk ? 'kg' : 'un'}</span>
        <span>Precio: ${item.unit_price.toLocaleString()}</span>
        <strong>Subtotal: ${item.line_total.toLocaleString()}</strong>
      </div>
      
      <button onClick={() => onRemove(item.id)} className="btn-remove">
        ❌
      </button>
    </div>
  );
};
```

---

## 🚨 Manejo de Errores

### **Errores Comunes**

```javascript
// Error 400 - Stock Insuficiente
{
  "detail": "Stock insuficiente para Arroz Diana 1kg. Disponible: 5, Solicitado: 10"
}

// Error 400 - Producto No Encontrado
{
  "detail": "Presentación con ID xxx no encontrada"
}

// Error 401 - No Autenticado
{
  "detail": "Usuario no identificado"
}

// Error 404 - Venta No Encontrada
{
  "detail": "Venta con ID xxx no encontrada"
}
```

### **Manejo en Frontend**

```javascript
const handleSaleError = (error) => {
  if (error.message.includes('Stock insuficiente')) {
    alert('⚠️ No hay suficiente stock para completar la venta. Por favor ajuste las cantidades.');
  } else if (error.message.includes('no encontrada')) {
    alert('❌ El producto seleccionado no está disponible. Por favor recargue la página.');
  } else if (error.message.includes('no identificado')) {
    alert('🔒 Su sesión ha expirado. Por favor inicie sesión nuevamente.');
    // Redirigir a login
  } else {
    alert(`❌ Error: ${error.message}`);
  }
};
```

---

## 📱 Servicio JavaScript Completo

```javascript
// services/salesService.js
class SalesService {
  constructor(baseURL = '/api/v1') {
    this.baseURL = baseURL;
  }
  
  getHeaders(token) {
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }
  
  // Crear venta
  async createSale(token, saleData) {
    const response = await fetch(`${this.baseURL}/sales/`, {
      method: 'POST',
      headers: this.getHeaders(token),
      body: JSON.stringify(saleData)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al crear venta');
    }
    
    return response.json();
  }
  
  // Obtener todas las ventas
  async getSales(token, skip = 0, limit = 100) {
    const response = await fetch(
      `${this.baseURL}/sales/?skip=${skip}&limit=${limit}`,
      { headers: this.getHeaders(token) }
    );
    
    if (!response.ok) {
      throw new Error('Error al obtener ventas');
    }
    
    return response.json();
  }
  
  // Obtener venta por ID
  async getSaleById(token, saleId) {
    const response = await fetch(`${this.baseURL}/sales/${saleId}`, {
      headers: this.getHeaders(token)
    });
    
    if (!response.ok) {
      throw new Error('Venta no encontrada');
    }
    
    return response.json();
  }
  
  // Obtener venta por código
  async getSaleByCode(token, saleCode) {
    const response = await fetch(`${this.baseURL}/sales/code/${saleCode}`, {
      headers: this.getHeaders(token)
    });
    
    if (!response.ok) {
      throw new Error('Venta no encontrada');
    }
    
    return response.json();
  }
  
  // Reporte de ventas
  async getSalesReport(token, filters = {}) {
    const params = new URLSearchParams();
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.customer_id) params.append('customer_id', filters.customer_id);
    if (filters.user_id) params.append('user_id', filters.user_id);
    
    const response = await fetch(
      `${this.baseURL}/sales/reports/summary?${params}`,
      { headers: this.getHeaders(token) }
    );
    
    if (!response.ok) {
      throw new Error('Error al generar reporte');
    }
    
    return response.json();
  }
  
  // Productos más vendidos
  async getBestSellingProducts(token, limit = 10) {
    const response = await fetch(
      `${this.baseURL}/sales/reports/best-products?limit=${limit}`,
      { headers: this.getHeaders(token) }
    );
    
    if (!response.ok) {
      throw new Error('Error al obtener productos más vendidos');
    }
    
    return response.json();
  }
  
  // Resumen diario
  async getDailySummary(token, date) {
    const dateStr = date instanceof Date ? date.toISOString() : date;
    const response = await fetch(
      `${this.baseURL}/sales/reports/daily/${dateStr}`,
      { headers: this.getHeaders(token) }
    );
    
    if (!response.ok) {
      throw new Error('Error al obtener resumen diario');
    }
    
    return response.json();
  }
}

export default new SalesService();
```

---

## 🎯 Casos de Uso Completos

### **Caso 1: Venta Solo de Productos Empaquetados**

```javascript
const saleData = {
  customer_id: "customer-uuid",
  status: "completed",
  items: [
    {
      presentation_id: "arroz-1kg-uuid",
      quantity: 5,
      unit_price: 4500.0
    },
    {
      presentation_id: "azucar-500g-uuid",
      quantity: 3,
      unit_price: 2800.0
    }
  ]
};

// Total esperado: (5 * 4500) + (3 * 2800) = 22500 + 8400 = 30900
```

### **Caso 2: Venta Solo a Granel**

```javascript
const saleData = {
  customer_id: "customer-uuid",
  status: "completed",
  items: [
    {
      presentation_id: "arroz-25kg-uuid", // Presentación que tiene stock a granel
      quantity: 7.5, // 7.5 kg
      unit_price: 3800.0 // Precio por kg
    }
  ]
};

// Total esperado: 7.5 * 3800 = 28500
```

### **Caso 3: Venta Mixta (Empaquetado + Granel) - AUTOMÁTICA**

```javascript
// El frontend simplemente envía la cantidad deseada
// El BACKEND decide automáticamente de dónde tomar el stock
const saleData = {
  customer_id: "customer-uuid",
  status: "completed",
  items: [
    {
      presentation_id: "arroz-1kg-uuid",
      quantity: 10, // Backend venderá de empaquetado Y granel si es necesario
      unit_price: 4500.0
    }
  ]
};

// Si hay solo 7 unidades empaquetadas y 5kg a granel disponibles:
// El backend creará automáticamente 2 SaleDetail:
// 1. lot_detail_id: "xxx", quantity: 7 (empaquetado)
// 2. bulk_conversion_id: "yyy", quantity: 3 (granel)
// Total en la respuesta: 10 unidades
```

### **Caso 4: Venta Mixta Múltiples Productos**

```javascript
const saleData = {
  customer_id: "customer-uuid",
  status: "completed",
  items: [
    {
      presentation_id: "arroz-1kg-uuid",
      quantity: 15, // Puede combinar empaquetado + granel
      unit_price: 4500.0
    },
    {
      presentation_id: "azucar-500g-uuid",
      quantity: 8, // Puede combinar empaquetado + granel
      unit_price: 2800.0
    },
    {
      presentation_id: "frijol-500g-uuid",
      quantity: 5, // Solo empaquetado si hay suficiente
      unit_price: 3200.0
    }
  ]
};

// El backend gestiona automáticamente cada item:
// - Arroz: 10 empaquetados + 5kg granel
// - Azúcar: 8 empaquetados
// - Frijol: 3 empaquetados + 2kg granel
// Todo en UNA SOLA VENTA
```

### **Caso 5: Error de Stock Insuficiente**

```javascript
// Si pides más de lo disponible (empaquetado + granel)
const saleData = {
  customer_id: "customer-uuid",
  status: "completed",
  items: [
    {
      presentation_id: "arroz-1kg-uuid",
      quantity: 100, // Solo hay 50 disponibles (empaquetado + granel)
      unit_price: 4500.0
    }
  ]
};

// Respuesta de error:
{
  "detail": "Stock insuficiente para Arroz Diana 1kg. Disponible: 50 (Empaquetado: 30, Granel: 20), Solicitado: 100"
}
```

---

## 🔧 Lógica Automática de Ventas Mixtas

### **¿Cómo Funciona Internamente?**

El backend implementa una **estrategia inteligente** para maximizar las ventas:

```
┌─────────────────────────────────────────────────────────────┐
│           ALGORITMO DE VENTA AUTOMÁTICA                     │
└─────────────────────────────────────────────────────────────┘

Para cada item en la venta:

1. OBTENER STOCK DISPONIBLE
   ├─ Stock Empaquetado (lot_detail.quantity_available)
   └─ Stock a Granel (bulk_conversion.remaining_bulk)

2. VALIDAR STOCK TOTAL
   Si (empaquetado + granel) < cantidad_solicitada:
      → ERROR: Stock insuficiente
   
3. VENDER DE EMPAQUETADO (FIFO)
   ├─ Buscar lotes con stock disponible
   ├─ Ordenar por fecha (más antiguos primero)
   └─ Vender hasta agotar cantidad o lotes
   
4. SI QUEDA CANTIDAD POR VENDER
   └─ VENDER DE GRANEL (FIFO)
      ├─ Buscar conversiones activas con stock
      ├─ Ordenar por fecha de conversión
      ├─ Vender hasta agotar cantidad
      └─ Marcar como COMPLETED si se agota

5. CREAR SALE_DETAILS
   ├─ Un SaleDetail por cada lote usado (empaquetado)
   └─ Un SaleDetail por cada conversión usada (granel)

6. CALCULAR TOTAL Y CONFIRMAR
```

### **Ejemplo Paso a Paso**

**Escenario:**
- Cliente pide: 15 unidades de "Arroz Diana 1kg"
- Stock disponible:
  - Lote A: 8 unidades empaquetadas
  - Lote B: 4 unidades empaquetadas
  - Conversión X: 5kg a granel

**Proceso:**

```
Cantidad solicitada: 15
Cantidad restante: 15

Paso 1: Vender de Lote A
  - Disponible: 8
  - Se vende: 8
  - Restante: 15 - 8 = 7
  - SaleDetail creado: lot_detail_id=A, quantity=8

Paso 2: Vender de Lote B
  - Disponible: 4
  - Se vende: 4
  - Restante: 7 - 4 = 3
  - SaleDetail creado: lot_detail_id=B, quantity=4

Paso 3: Vender de Conversión X
  - Disponible: 5kg
  - Se vende: 3kg
  - Restante: 3 - 3 = 0 ✅
  - SaleDetail creado: bulk_conversion_id=X, quantity=3
  - Conversión X queda con: 2kg remaining_bulk

Resultado:
  - 3 SaleDetails creados
  - Total vendido: 15 unidades
  - Empaquetado: 12, Granel: 3
```

---

### **Caso 3: Venta Mixta (Empaquetado + Granel) - AUTOMÁTICA**

```javascript
// El frontend simplemente envía la cantidad deseada
// El BACKEND decide automáticamente de dónde tomar el stock
const saleData = {
  customer_id: "customer-uuid",
  status: "completed",
  items: [
    {
      presentation_id: "arroz-1kg-uuid",
      quantity: 10, // Backend venderá de empaquetado Y granel si es necesario
      unit_price: 4500.0
    }
  ]
};

// Si hay solo 7 unidades empaquetadas y 5kg a granel disponibles:
// El backend creará automáticamente 2 SaleDetail:
// 1. lot_detail_id: "xxx", quantity: 7 (empaquetado)
// 2. bulk_conversion_id: "yyy", quantity: 3 (granel)
// Total en la respuesta: 10 unidades
```

### **Caso 4: Venta Mixta Múltiples Productos**

```javascript
const saleData = {
  customer_id: "customer-uuid",
  status: "completed",
  items: [
    {
      presentation_id: "arroz-1kg-uuid",
      quantity: 15, // Puede combinar empaquetado + granel
      unit_price: 4500.0
    },
    {
      presentation_id: "azucar-500g-uuid",
      quantity: 8, // Puede combinar empaquetado + granel
      unit_price: 2800.0
    },
    {
      presentation_id: "frijol-500g-uuid",
      quantity: 5, // Solo empaquetado si hay suficiente
      unit_price: 3200.0
    }
  ]
};

// El backend gestiona automáticamente cada item:
// - Arroz: 10 empaquetados + 5kg granel
// - Azúcar: 8 empaquetados
// - Frijol: 3 empaquetados + 2kg granel
// Todo en UNA SOLA VENTA
```

### **Caso 5: Error de Stock Insuficiente**

```javascript
// Si pides más de lo disponible (empaquetado + granel)
const saleData = {
  customer_id: "customer-uuid",
  status: "completed",
  items: [
    {
      presentation_id: "arroz-1kg-uuid",
      quantity: 100, // Solo hay 50 disponibles (empaquetado + granel)
      unit_price: 4500.0
    }
  ]
};

// Respuesta de error:
{
  "detail": "Stock insuficiente para Arroz Diana 1kg. Disponible: 50 (Empaquetado: 30, Granel: 20), Solicitado: 100"
}
```

---

## ✅ Checklist de Implementación

- [ ] **Autenticación configurada** - Token JWT en headers
- [ ] **Cargar clientes** - GET /api/v1/persons/
- [ ] **Cargar productos** - GET /api/v1/products/
- [ ] **Filtrar productos con stock** - current_stock > 0 o bulk_stock_available > 0
- [ ] **Diferenciar empaquetado vs granel** - Usar campos is_bulk_source y can_sell_bulk
- [ ] **Validar stock antes de agregar** - Comparar con current_stock o bulk_stock_available
- [ ] **Calcular subtotales** - quantity * unit_price
- [ ] **Calcular total** - Suma de todos los line_total
- [ ] **Enviar venta** - POST /api/v1/sales/ con estructura correcta
- [ ] **Manejar errores** - Stock insuficiente, producto no encontrado, etc.
- [ ] **Mostrar confirmación** - sale_code, total, fecha
- [ ] **Actualizar stock** - Recargar productos después de venta
- [ ] **Limpiar carrito** - Resetear estado después de venta exitosa

---

## 🔍 Tips y Mejores Prácticas

### **1. Validación de Stock en Tiempo Real**

```javascript
// Verificar stock antes de procesar venta
const validateStock = async (items) => {
  const products = await loadProducts();
  
  for (const item of items) {
    const product = products.find(p => 
      p.presentations.some(pres => pres.id === item.presentation_id)
    );
    
    const presentation = product?.presentations.find(
      pres => pres.id === item.presentation_id
    );
    
    const availableStock = item.is_bulk 
      ? presentation.bulk_stock_available 
      : presentation.current_stock;
    
    if (item.quantity > availableStock) {
      throw new Error(
        `Stock insuficiente para ${presentation.name}. ` +
        `Disponible: ${availableStock}, Solicitado: ${item.quantity}`
      );
    }
  }
};
```

### **2. Formateo de Precios**

```javascript
const formatPrice = (price) => {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0
  }).format(price);
};

// Uso: formatPrice(34500) => "$34.500"
```

### **3. Manejo de Decimales en Granel**

```javascript
// Permitir decimales solo para ventas a granel
<input
  type="number"
  min="0.1"
  step={isBulk ? "0.1" : "1"}
  value={quantity}
  onChange={(e) => {
    const value = parseFloat(e.target.value);
    setQuantity(isBulk ? value : Math.floor(value));
  }}
/>
```

### **4. Confirmación antes de Procesar**

```javascript
const confirmSale = () => {
  const total = calculateTotal();
  const itemCount = cart.length;
  
  const confirmed = window.confirm(
    `¿Confirmar venta?\n\n` +
    `Cliente: ${selectedCustomer.full_name}\n` +
    `Items: ${itemCount}\n` +
    `Total: ${formatPrice(total)}`
  );
  
  if (confirmed) {
    processSale();
  }
};
```

---

## 📊 Dashboard de Ventas (Ejemplo)

```jsx
const SalesDashboard = () => {
  const [summary, setSummary] = useState(null);
  const [bestProducts, setBestProducts] = useState([]);
  const token = localStorage.getItem('token');
  
  useEffect(() => {
    loadDashboardData();
  }, []);
  
  const loadDashboardData = async () => {
    try {
      // Reporte del mes actual
      const startOfMonth = new Date();
      startOfMonth.setDate(1);
      startOfMonth.setHours(0, 0, 0, 0);
      
      const endOfMonth = new Date();
      endOfMonth.setMonth(endOfMonth.getMonth() + 1);
      endOfMonth.setDate(0);
      endOfMonth.setHours(23, 59, 59, 999);
      
      const [reportData, productsData] = await Promise.all([
        SalesService.getSalesReport(token, {
          start_date: startOfMonth.toISOString(),
          end_date: endOfMonth.toISOString()
        }),
        SalesService.getBestSellingProducts(token, 5)
      ]);
      
      setSummary(reportData);
      setBestProducts(productsData.best_selling_products);
      
    } catch (error) {
      console.error('Error:', error);
    }
  };
  
  return (
    <div className="dashboard">
      <h1>📊 Dashboard de Ventas</h1>
      
      {summary && (
        <div className="summary-cards">
          <div className="card">
            <h3>Total Ventas</h3>
            <p className="big-number">{summary.total_sales}</p>
          </div>
          
          <div className="card">
            <h3>Ingresos Totales</h3>
            <p className="big-number">{formatPrice(summary.total_revenue)}</p>
          </div>
          
          <div className="card">
            <h3>Venta Promedio</h3>
            <p className="big-number">
              {formatPrice(summary.total_revenue / summary.total_sales)}
            </p>
          </div>
        </div>
      )}
      
      {bestProducts.length > 0 && (
        <div className="best-products">
          <h2>🏆 Productos Más Vendidos</h2>
          <table>
            <thead>
              <tr>
                <th>Producto</th>
                <th>Cantidad Vendida</th>
                <th>Ingresos</th>
              </tr>
            </thead>
            <tbody>
              {bestProducts.map(product => (
                <tr key={product.presentation_id}>
                  <td>{product.presentation_name}</td>
                  <td>{product.total_sold}</td>
                  <td>{formatPrice(product.total_revenue)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
```

---

## 🎨 Estilos CSS Recomendados

```css
/* Sales Module Styles */
.sales-module {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.customer-section {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.customer-section select {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.products-section {
  margin-bottom: 30px;
}

.product-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
}

.product-card h3 {
  margin-top: 0;
  color: #333;
}

.category {
  color: #666;
  font-size: 14px;
}

.stock-info {
  margin: 10px 0;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 4px;
}

.cart-section {
  background: #fff;
  border: 2px solid #4CAF50;
  border-radius: 8px;
  padding: 20px;
  position: sticky;
  top: 20px;
}

.cart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.cart-total {
  margin: 20px 0;
  padding: 15px;
  background: #f0f0f0;
  border-radius: 4px;
  text-align: right;
  font-size: 20px;
}

.btn-process-sale {
  width: 100%;
  padding: 15px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 18px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-process-sale:hover:not(:disabled) {
  background: #45a049;
}

.btn-process-sale:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.btn-add {
  background: #2196F3;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-remove {
  background: #f44336;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
}
```

---

## 🚀 Conclusión

Este documento cubre todo lo necesario para implementar el sistema de ventas completo en el frontend:

✅ **Endpoints documentados** con ejemplos de request/response  
✅ **Flujo de trabajo** paso a paso  
✅ **Componentes React** completos y funcionales  
✅ **Servicio JavaScript** para comunicación con API  
✅ **Manejo de errores** robusto  
✅ **Casos de uso** reales con ejemplos  
✅ **Mejores prácticas** y tips de implementación  

**¿Necesitas algo más?** Contáctame para soporte adicional.

---

**Última actualización:** Octubre 12, 2025  
**Versión del Backend:** 1.0  
**Endpoints Base:** `/api/v1/`

---

## 🎯 Resumen Ejecutivo

### **Características Principales**

✅ **Ventas Mixtas Automáticas** - El sistema combina automáticamente stock empaquetado y granel en una sola venta  
✅ **Estrategia FIFO** - First In, First Out para optimizar rotación de inventario  
✅ **Validación Inteligente** - Verifica stock total (empaquetado + granel) antes de procesar  
✅ **Múltiples SaleDetails** - Un mismo producto puede generar varios registros si usa diferentes orígenes  
✅ **Cancelación Completa** - Restaura tanto stock empaquetado como a granel  
✅ **Reportes Integrados** - Dashboard con productos más vendidos, resúmenes diarios, etc.

### **¿Qué hace el Backend Automáticamente?**

| Frontend Envía | Backend Hace |
|----------------|--------------|
| `quantity: 10` | 1. Busca lotes empaquetados (FIFO)<br>2. Vende lo disponible<br>3. Si falta, busca stock a granel<br>4. Vende lo que falta<br>5. Crea múltiples SaleDetails si es necesario |
| Un solo `item` | Puede generar 2+ `SaleDetail` en respuesta |
| Stock validation | Valida empaquetado + granel juntos |

### **Frontend NO necesita:**

❌ Especificar si quiere venta empaquetada o granel  
❌ Hacer cálculos de disponibilidad por tipo  
❌ Crear múltiples items para el mismo producto  
❌ Preocuparse por la lógica FIFO  

### **Frontend SÍ debe:**

✅ Mostrar stock total (`current_stock + bulk_stock_available`)  
✅ Validar que la cantidad no exceda el total  
✅ Agrupar items en respuesta si necesita mostrar por producto  
✅ Interpretar `lot_detail_id` vs `bulk_conversion_id` si quiere diferenciar origen  

### **Pregunta Clave Respondida**

**¿Se puede en una sola venta registrar productos empaquetados Y a granel?**

**SÍ** ✅ - El sistema lo hace **AUTOMÁTICAMENTE**:
- El frontend solo envía la cantidad deseada
- El backend decide inteligentemente de dónde tomar el stock
- Puede combinar ambos tipos sin que el frontend lo especifique
- Todo en una sola transacción atómica

---

**¿Necesitas más información?** Revisa las secciones anteriores o contacta al equipo de backend.
