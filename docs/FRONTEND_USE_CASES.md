# 📋 Casos de Uso y Flujos de Trabajo Frontend

## 🎯 Casos de Uso Principales

### 1. 🔐 Autenticación de Usuario
**Actor:** Usuario del sistema  
**Objetivo:** Acceder al sistema de ventas e inventario

**Flujo Principal:**
1. Usuario ingresa email y contraseña
2. Sistema valida credenciales con Firebase
3. Sistema obtiene información del usuario desde BD
4. Sistema guarda token y datos del usuario
5. Usuario accede al dashboard principal

**Implementación:**
```javascript
// Caso de uso: Login
async function loginUser(email, password) {
  try {
    showLoading('login-form');
    
    const response = await api.login(email, password);
    
    // Guardar datos del usuario
    localStorage.setItem('user', JSON.stringify(response.user));
    
    // Redirigir al dashboard
    window.location.href = '/dashboard';
    
    showNotification('Bienvenido ' + response.user.person.first_name, 'success');
  } catch (error) {
    showNotification('Error de autenticación: ' + error.message, 'error');
  } finally {
    hideLoading('login-form');
  }
}
```

---

### 2. 💰 Proceso de Venta Completo
**Actor:** Vendedor  
**Objetivo:** Registrar una venta y actualizar el inventario

**Flujo Principal:**
1. Vendedor selecciona cliente
2. Vendedor busca y agrega productos al carrito
3. Sistema valida stock disponible
4. Vendedor confirma cantidades y precios
5. Sistema procesa la venta
6. Sistema actualiza inventario automáticamente
7. Sistema genera código de venta
8. Vendedor entrega productos

**Implementación Completa:**
```javascript
class SalesWorkflow {
  constructor() {
    this.cart = new ShoppingCart();
    this.selectedCustomer = null;
    this.state = 'idle'; // idle, selecting-customer, adding-products, processing
  }

  // Paso 1: Seleccionar cliente
  async selectCustomer(customerId) {
    try {
      this.state = 'selecting-customer';
      
      const customer = await api.getCustomerById(customerId);
      this.selectedCustomer = customer;
      
      this.updateUI();
      this.state = 'adding-products';
      
    } catch (error) {
      this.handleError('Error al seleccionar cliente', error);
    }
  }

  // Paso 2: Agregar productos
  async addProduct(presentationId, quantity, unitPrice) {
    try {
      // Validar stock
      const stock = await api.getStock(presentationId);
      
      if (stock.available_stock < quantity) {
        throw new Error(`Stock insuficiente. Disponible: ${stock.available_stock}`);
      }
      
      // Obtener información del producto
      const presentation = await api.getPresentationById(presentationId);
      
      // Agregar al carrito
      this.cart.addItem({
        presentation,
        quantity,
        unitPrice,
        lineTotal: quantity * unitPrice
      });
      
      this.updateUI();
      
    } catch (error) {
      this.handleError('Error al agregar producto', error);
    }
  }

  // Paso 3: Procesar venta
  async processSale() {
    try {
      this.state = 'processing';
      this.updateUI();
      
      // Validaciones finales
      if (!this.selectedCustomer) {
        throw new Error('Debe seleccionar un cliente');
      }
      
      if (this.cart.isEmpty()) {
        throw new Error('El carrito está vacío');
      }
      
      // Verificar stock de todos los productos
      await this.validateAllStock();
      
      // Crear la venta
      const saleData = {
        customer_id: this.selectedCustomer.id,
        status: 'completed',
        items: this.cart.getItems().map(item => ({
          presentation_id: item.presentation.id,
          quantity: item.quantity,
          unit_price: item.unitPrice
        }))
      };
      
      const sale = await api.createSale(saleData);
      
      // Mostrar resultado
      this.showSaleSuccess(sale);
      
      // Limpiar carrito
      this.resetWorkflow();
      
      return sale;
      
    } catch (error) {
      this.handleError('Error al procesar venta', error);
      this.state = 'adding-products';
    }
  }

  async validateAllStock() {
    for (const item of this.cart.getItems()) {
      const stock = await api.getStock(item.presentation.id);
      if (stock.available_stock < item.quantity) {
        throw new Error(
          `Stock insuficiente para ${item.presentation.presentation_name}. ` +
          `Disponible: ${stock.available_stock}, Solicitado: ${item.quantity}`
        );
      }
    }
  }

  showSaleSuccess(sale) {
    showNotification(
      `Venta procesada exitosamente: ${sale.sale_code}`,
      'success'
    );
    
    // Imprimir comprobante (opcional)
    if (confirm('¿Desea imprimir el comprobante?')) {
      this.printReceipt(sale);
    }
  }

  resetWorkflow() {
    this.cart.clear();
    this.selectedCustomer = null;
    this.state = 'idle';
    this.updateUI();
  }

  updateUI() {
    // Actualizar interfaz según el estado
    document.getElementById('customer-info').style.display = 
      this.selectedCustomer ? 'block' : 'none';
    
    document.getElementById('cart-summary').innerHTML = 
      this.cart.getSummaryHTML();
    
    document.getElementById('process-btn').disabled = 
      !this.selectedCustomer || this.cart.isEmpty() || this.state === 'processing';
  }
}
```

---

### 3. 📦 Gestión de Inventario - Recepción de Mercancía
**Actor:** Encargado de almacén  
**Objetivo:** Registrar nuevos productos en el inventario

**Flujo Principal:**
1. Encargado recibe mercancía del proveedor
2. Crea nuevo lote con información del proveedor
3. Registra cada producto con cantidades y fechas
4. Sistema actualiza stock disponible
5. Sistema genera reporte de recepción

**Implementación:**
```javascript
class InventoryReception {
  constructor() {
    this.currentLot = null;
    this.receivedProducts = [];
  }

  // Paso 1: Crear lote
  async createLot(supplierI, lotCode, receivedDate) {
    try {
      const lotData = {
        supplier_id: supplierId,
        received_date: receivedDate,
        lot_code: lotCode,
        status: 'active'
      };
      
      this.currentLot = await api.createLot(lotData);
      
      showNotification(`Lote ${lotCode} creado exitosamente`, 'success');
      this.updateLotInfo();
      
    } catch (error) {
      this.handleError('Error al crear lote', error);
    }
  }

  // Paso 2: Agregar productos al lote
  async addProductToLot(presentationId, quantity, unitCost, expirationDate) {
    try {
      if (!this.currentLot) {
        throw new Error('Debe crear un lote primero');
      }
      
      const productData = {
        presentation_id: presentationId,
        quantity_received: quantity,
        unit_cost: unitCost,
        expiration_date: expirationDate,
        production_date: new Date().toISOString()
      };
      
      const lotDetail = await api.addProductsToLot(this.currentLot.id, productData);
      
      this.receivedProducts.push(lotDetail);
      this.updateProductsList();
      
      showNotification('Producto agregado al lote', 'success');
      
    } catch (error) {
      this.handleError('Error al agregar producto', error);
    }
  }

  // Paso 3: Finalizar recepción
  async finalizeLot() {
    try {
      if (this.receivedProducts.length === 0) {
        throw new Error('Debe agregar al menos un producto');
      }
      
      // Generar resumen
      const summary = this.generateSummary();
      
      // Mostrar confirmación
      if (confirm(`¿Finalizar recepción del lote ${this.currentLot.lot_code}?`)) {
        showNotification('Lote finalizado exitosamente', 'success');
        this.printSummary(summary);
        this.reset();
      }
      
    } catch (error) {
      this.handleError('Error al finalizar lote', error);
    }
  }

  generateSummary() {
    const totalProducts = this.receivedProducts.length;
    const totalQuantity = this.receivedProducts.reduce(
      (sum, product) => sum + product.quantity_received, 0
    );
    const totalCost = this.receivedProducts.reduce(
      (sum, product) => sum + (product.quantity_received * product.unit_cost), 0
    );

    return {
      lotCode: this.currentLot.lot_code,
      totalProducts,
      totalQuantity,
      totalCost,
      products: this.receivedProducts
    };
  }
}
```

---

### 4. 📊 Generación de Reportes
**Actor:** Gerente/Administrador  
**Objetivo:** Obtener información sobre ventas e inventario

**Flujo Principal:**
1. Usuario selecciona tipo de reporte
2. Usuario especifica filtros (fechas, productos, clientes)
3. Sistema genera el reporte
4. Usuario visualiza datos
5. Usuario puede exportar o imprimir

**Implementación:**
```javascript
class ReportsManager {
  constructor() {
    this.currentReport = null;
    this.filters = {};
  }

  // Reporte de ventas por período
  async generateSalesReport(startDate, endDate, customerId = null) {
    try {
      showLoading('reports-container');
      
      const filters = {
        start_date: startDate,
        end_date: endDate,
        ...(customerId && { customer_id: customerId })
      };
      
      const report = await api.getSalesReport(filters);
      
      this.currentReport = {
        type: 'sales',
        data: report,
        filters,
        generatedAt: new Date().toISOString()
      };
      
      this.renderSalesReport(report);
      
    } catch (error) {
      this.handleError('Error al generar reporte de ventas', error);
    } finally {
      hideLoading('reports-container');
    }
  }

  // Reporte de productos más vendidos
  async generateBestSellersReport(limit = 10) {
    try {
      const report = await api.getBestSellingProducts(limit);
      
      this.currentReport = {
        type: 'best-sellers',
        data: report,
        generatedAt: new Date().toISOString()
      };
      
      this.renderBestSellersReport(report);
      
    } catch (error) {
      this.handleError('Error al generar reporte de más vendidos', error);
    }
  }

  // Reporte de inventario
  async generateInventoryReport() {
    try {
      const categories = await api.getCategories();
      const inventoryData = [];
      
      for (const category of categories) {
        const products = await api.getProductsByCategory(category.id);
        
        for (const product of products) {
          for (const presentation of product.presentations) {
            const stock = await api.getStock(presentation.id);
            inventoryData.push({
              category: category.name,
              product: product.name,
              presentation: presentation.presentation_name,
              stock: stock.available_stock,
              nextExpiration: stock.next_expiration
            });
          }
        }
      }
      
      this.currentReport = {
        type: 'inventory',
        data: inventoryData,
        generatedAt: new Date().toISOString()
      };
      
      this.renderInventoryReport(inventoryData);
      
    } catch (error) {
      this.handleError('Error al generar reporte de inventario', error);
    }
  }

  // Exportar reporte a CSV
  exportToCSV() {
    if (!this.currentReport) {
      showNotification('No hay reporte para exportar', 'warning');
      return;
    }
    
    let csvContent = '';
    
    switch (this.currentReport.type) {
      case 'sales':
        csvContent = this.generateSalesCSV(this.currentReport.data);
        break;
      case 'best-sellers':
        csvContent = this.generateBestSellersCSV(this.currentReport.data);
        break;
      case 'inventory':
        csvContent = this.generateInventoryCSV(this.currentReport.data);
        break;
    }
    
    this.downloadCSV(csvContent, `${this.currentReport.type}-report.csv`);
  }

  generateSalesCSV(data) {
    const headers = ['Código Venta', 'Fecha', 'Cliente', 'Total', 'Estado'];
    const rows = data.sales.map(sale => [
      sale.sale_code,
      new Date(sale.sale_date).toLocaleDateString(),
      sale.customer_name || sale.customer_id,
      sale.total,
      sale.status
    ]);
    
    return this.arrayToCSV([headers, ...rows]);
  }

  downloadCSV(content, filename) {
    const blob = new Blob([content], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  }
}
```

---

### 5. 🔍 Búsqueda y Filtrado de Productos
**Actor:** Vendedor  
**Objetivo:** Encontrar productos específicos para agregar a una venta

**Flujo Principal:**
1. Usuario ingresa término de búsqueda o selecciona categoría
2. Sistema muestra productos que coinciden
3. Usuario ve detalles del producto (stock, precio, etc.)
4. Usuario selecciona cantidad y agrega al carrito

**Implementación:**
```javascript
class ProductSearch {
  constructor() {
    this.searchResults = [];
    this.filters = {
      category: null,
      searchTerm: '',
      inStock: true
    };
  }

  async searchProducts(searchTerm = '', categoryId = null) {
    try {
      showLoading('products-grid');
      
      this.filters.searchTerm = searchTerm;
      this.filters.category = categoryId;
      
      let products = [];
      
      if (categoryId) {
        products = await api.getProductsByCategory(categoryId);
      } else {
        products = await api.searchProducts(searchTerm);
      }
      
      // Enriquecer con información de stock
      const productsWithStock = await this.enrichWithStock(products);
      
      // Aplicar filtros adicionales
      this.searchResults = this.applyFilters(productsWithStock);
      
      this.renderResults();
      
    } catch (error) {
      this.handleError('Error en búsqueda', error);
    } finally {
      hideLoading('products-grid');
    }
  }

  async enrichWithStock(products) {
    const enrichedProducts = [];
    
    for (const product of products) {
      const enrichedPresentations = [];
      
      for (const presentation of product.presentations) {
        try {
          const stock = await api.getStock(presentation.id);
          enrichedPresentations.push({
            ...presentation,
            stock: stock.available_stock,
            nextExpiration: stock.next_expiration
          });
        } catch (error) {
          console.warn(`Error getting stock for ${presentation.id}`);
          enrichedPresentations.push({
            ...presentation,
            stock: 0
          });
        }
      }
      
      enrichedProducts.push({
        ...product,
        presentations: enrichedPresentations
      });
    }
    
    return enrichedProducts;
  }

  applyFilters(products) {
    return products.filter(product => {
      // Filtrar por stock si está activado
      if (this.filters.inStock) {
        const hasStock = product.presentations.some(p => p.stock > 0);
        if (!hasStock) return false;
      }
      
      return true;
    });
  }

  renderResults() {
    const container = document.getElementById('products-grid');
    container.innerHTML = '';
    
    if (this.searchResults.length === 0) {
      container.innerHTML = '<p>No se encontraron productos</p>';
      return;
    }
    
    this.searchResults.forEach(product => {
      const productCard = this.createProductCard(product);
      container.appendChild(productCard);
    });
  }

  createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    card.innerHTML = `
      <h3>${product.name}</h3>
      <p>${product.description || ''}</p>
      <div class="presentations">
        ${product.presentations.map(p => `
          <div class="presentation ${p.stock === 0 ? 'out-of-stock' : ''}">
            <span class="name">${p.presentation_name}</span>
            <span class="stock">Stock: ${p.stock}</span>
            <button 
              onclick="addToCart('${p.id}', 1)" 
              ${p.stock === 0 ? 'disabled' : ''}
            >
              Agregar
            </button>
          </div>
        `).join('')}
      </div>
    `;
    
    return card;
  }
}
```

---

## 🎮 Interfaz de Usuario - Flujos de Navegación

### Dashboard Principal
```
┌─────────────────────────────────────────────────┐
│ MAPO - Dashboard                    [Usuario] ↓ │
├─────────────────────────────────────────────────┤
│ [Ventas] [Inventario] [Reportes] [Configuración]│
├─────────────────────────────────────────────────┤
│                                                 │
│  Resumen del Día:                              │
│  ├─ Ventas: $1,250.00 (8 ventas)              │
│  ├─ Productos más vendidos                     │
│  └─ Alertas de stock bajo                      │
│                                                 │
│  Acciones Rápidas:                            │
│  ├─ [Nueva Venta]                             │
│  ├─ [Recibir Mercancía]                       │
│  └─ [Ver Reportes]                            │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Interfaz de Ventas
```
┌─────────────────────────────────────────────────┐
│ Nueva Venta                            [Volver] │
├─────────────────────────────────────────────────┤
│ Cliente: [Seleccionar Cliente ↓] [Nuevo Cliente]│
├─────────────────────────────────────────────────┤
│ PRODUCTOS                   │ CARRITO            │
│ ┌─────────────────────────┐ │ ┌─────────────────┐│
│ │ [Buscar...]             │ │ │Cliente: Juan P. ││
│ │ [Categoría ↓]           │ │ │                 ││
│ │                         │ │ │ 2x Coca Cola    ││
│ │ [Producto 1] [Agregar]  │ │ │    $3.00        ││
│ │ [Producto 2] [Agregar]  │ │ │ 1x Papitas      ││
│ │ [Producto 3] [Agregar]  │ │ │    $2.50        ││
│ │                         │ │ │                 ││
│ └─────────────────────────┘ │ │ Total: $5.50    ││
│                             │ │                 ││
│                             │ │ [Procesar Venta]││
│                             │ └─────────────────┘│
└─────────────────────────────────────────────────┘
```

### Estados de Loading y Feedback
```javascript
// Ejemplo de estados visuales
const UIStates = {
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error',
  EMPTY: 'empty'
};

function updateUIState(elementId, state, message = '') {
  const element = document.getElementById(elementId);
  
  switch (state) {
    case UIStates.LOADING:
      element.innerHTML = `
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Cargando...</p>
        </div>
      `;
      break;
      
    case UIStates.SUCCESS:
      element.classList.add('success-state');
      showNotification(message || 'Operación exitosa', 'success');
      break;
      
    case UIStates.ERROR:
      element.innerHTML = `
        <div class="error-state">
          <p>❌ ${message || 'Error en la operación'}</p>
          <button onclick="retry()">Reintentar</button>
        </div>
      `;
      break;
      
    case UIStates.EMPTY:
      element.innerHTML = `
        <div class="empty-state">
          <p>No hay datos para mostrar</p>
        </div>
      `;
      break;
  }
}
```

Estos casos de uso cubren todos los flujos principales del sistema MAPO, proporcionando una guía completa para la implementación del frontend. Cada flujo incluye validaciones, manejo de errores y feedback visual apropiado. 🎯