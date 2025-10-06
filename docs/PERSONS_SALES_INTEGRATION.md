# 👥 Integración de Personas en Sistema de Ventas

## 📋 Información General

Este documento explica cómo usar los endpoints de **Personas** para implementar correctamente el sistema de ventas en el frontend, incluyendo la gestión de clientes y usuarios.

## 🔗 Endpoints Disponibles

### **1. Obtener Todas las Personas**
```http
GET /api/v1/persons/
```

**Respuesta:**
```json
[
  {
    "id": "67825f4c-e43f-4871-8b46-6016ceebbecf",
    "name": "Juan Carlos",
    "last_name": "Pérez García",
    "document_type": "CC",
    "document_number": "12345678",
    "full_name": "Juan Carlos Pérez García"
  },
  {
    "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "name": "María Elena",
    "last_name": "Rodríguez López",
    "document_type": "CE",
    "document_number": "87654321",
    "full_name": "María Elena Rodríguez López"
  }
]
```

### **2. Obtener Persona por ID**
```http
GET /api/v1/persons/{person_id}
```

**Ejemplo:**
```http
GET /api/v1/persons/67825f4c-e43f-4871-8b46-6016ceebbecf
```

**Respuesta:**
```json
{
  "id": "67825f4c-e43f-4871-8b46-6016ceebbecf",
  "name": "Juan Carlos",
  "last_name": "Pérez García", 
  "document_type": "CC",
  "document_number": "12345678",
  "full_name": "Juan Carlos Pérez García"
}
```

### **3. ✨ NUEVO: Registrar Persona/Cliente**
```http
POST /api/v1/persons/
```

**🎯 Endpoint PÚBLICO - No requiere autenticación**

Este endpoint permite registrar rápidamente nuevos clientes sin necesidad de crear cuentas de usuario.

**Body de la solicitud:**
```json
{
  "name": "Ana María",
  "last_name": "González Herrera",
  "document_type": "CC",
  "document_number": "98765432",
  "phone": "+57 300 123 4567",
  "email": "ana.gonzalez@email.com",
  "address": "Calle 45 #12-34, Bogotá"
}
```

**Campos requeridos:**
- `name`: string (mínimo 2 caracteres)
- `last_name`: string (mínimo 2 caracteres)  
- `document_type`: string ("CC", "CE", "TI", "PP", "NIT")
- `document_number`: string (único por tipo)

**Campos opcionales:**
- `phone`: string
- `email`: string (único, formato email)
- `address`: string

**Respuesta exitosa (201):**
```json
{
  "message": "Persona creada exitosamente",
  "person": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "name": "Ana María",
    "last_name": "González Herrera",
    "document_type": "CC",
    "document_number": "98765432",
    "phone": "+57 300 123 4567",
    "email": "ana.gonzalez@email.com",
    "address": "Calle 45 #12-34, Bogotá",
    "full_name": "Ana María González Herrera"
  }
}
```

**Posibles errores:**
```json
// Error 400 - Documento duplicado
{
  "detail": "Ya existe una persona con CC: 98765432"
}

// Error 400 - Email duplicado
{
  "detail": "Ya existe una persona con el email: ana.gonzalez@email.com"
}
```

### **4. Búsqueda de Personas**
```http
GET /api/v1/persons/?search=término
```

**Ejemplo:**
```http
GET /api/v1/persons/?search=Juan
GET /api/v1/persons/?search=12345678
GET /api/v1/persons/?search=juan@email.com
```

## 🛒 Implementación en Sistema de Ventas

### **1. Selector de Cliente en Ventas**

```jsx
// Componente para seleccionar cliente en venta
import React, { useState, useEffect } from 'react';

const CustomerSelector = ({ onCustomerSelect, selectedCustomerId }) => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Cargar todas las personas al montar el componente
  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/persons/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const persons = await response.json();
        setCustomers(persons);
      } else {
        console.error('Error al cargar clientes');
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Filtrar clientes por búsqueda
  const filteredCustomers = customers.filter(customer => 
    customer.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.document_number.includes(searchTerm)
  );

  return (
    <div className="customer-selector">
      <label>Seleccionar Cliente:</label>
      
      {/* Buscador */}
      <input
        type="text"
        placeholder="Buscar por nombre o documento..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="search-input"
      />

      {/* Lista de clientes */}
      {loading ? (
        <div>Cargando clientes...</div>
      ) : (
        <select 
          value={selectedCustomerId || ''} 
          onChange={(e) => onCustomerSelect(e.target.value)}
          className="customer-select"
        >
          <option value="">-- Seleccione un cliente --</option>
          {filteredCustomers.map(customer => (
            <option key={customer.id} value={customer.id}>
              {customer.full_name} - {customer.document_type}: {customer.document_number}
            </option>
          ))}
        </select>
      )}

      {/* Información del cliente seleccionado */}
      {selectedCustomerId && (
        <div className="selected-customer-info">
          {(() => {
            const selected = customers.find(c => c.id === selectedCustomerId);
            return selected ? (
              <div className="customer-info">
                <strong>Cliente Seleccionado:</strong>
                <br />
                📋 {selected.full_name}
                <br />
                🆔 {selected.document_type}: {selected.document_number}
              </div>
            ) : null;
          })()}
        </div>
      )}
    </div>
  );
};

export default CustomerSelector;
```

### **2. Integración en Formulario de Venta**

```jsx
// Componente principal de venta
const SaleForm = () => {
  const [saleData, setSaleData] = useState({
    customerId: '',
    userId: '', // Se obtiene del usuario logueado
    items: [],
    total: 0
  });

  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    // Obtener usuario actual
    const getUserInfo = async () => {
      const response = await fetch('/api/v1/users/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const user = await response.json();
      setCurrentUser(user);
      setSaleData(prev => ({ ...prev, userId: user.id }));
    };
    
    getUserInfo();
  }, []);

  const handleCustomerSelect = (customerId) => {
    setSaleData(prev => ({ ...prev, customerId }));
  };

  const handleSale = async () => {
    if (!saleData.customerId) {
      alert('Debe seleccionar un cliente');
      return;
    }

    try {
      // Para venta a granel
      const bulkSaleData = {
        bulk_conversion_id: "bulk-uuid-here",
        quantity: 5,
        unit_price: 3800,
        customer_id: saleData.customerId,
        user_id: saleData.userId
      };

      const response = await fetch('/api/v1/products/sell-bulk/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(bulkSaleData)
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Venta exitosa:', result);
        // Resetear formulario o redirigir
      }
    } catch (error) {
      console.error('Error en venta:', error);
    }
  };

  return (
    <div className="sale-form">
      <h2>🛒 Nueva Venta</h2>
      
      {/* Selector de Cliente */}
      <CustomerSelector 
        onCustomerSelect={handleCustomerSelect}
        selectedCustomerId={saleData.customerId}
      />

      {/* Información del vendedor */}
      {currentUser && (
        <div className="seller-info">
          <strong>Vendedor:</strong> {currentUser.name} {currentUser.last_name}
        </div>
      )}

      {/* Productos y resto del formulario... */}
      
      <button onClick={handleSale} disabled={!saleData.customerId}>
        Procesar Venta
      </button>
    </div>
  );
};
```

### **3. Servicio para Gestión de Personas**

```javascript
// services/personService.js
class PersonService {
  constructor(baseURL, token) {
    this.baseURL = baseURL;
    this.token = token;
  }

  async getAllPersons() {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/persons/`, {
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error al obtener personas:', error);
      throw error;
    }
  }

  async getPersonById(personId) {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/persons/${personId}`, {
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error al obtener persona:', error);
      throw error;
    }
  }

  // Buscar personas por término
  async searchPersons(searchTerm, persons = null) {
    // Si no se proveen personas, obtenerlas primero
    if (!persons) {
      persons = await this.getAllPersons();
    }

    return persons.filter(person => 
      person.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      person.document_number.includes(searchTerm) ||
      person.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      person.last_name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }

  // Formatear persona para mostrar
  formatPersonForDisplay(person) {
    return `${person.full_name} (${person.document_type}: ${person.document_number})`;
  }
}

// Uso del servicio
const personService = new PersonService('http://localhost:8000', authToken);

// Ejemplo de uso
const loadCustomersForSale = async () => {
  try {
    const persons = await personService.getAllPersons();
    console.log('Clientes disponibles:', persons);
    return persons;
  } catch (error) {
    console.error('Error al cargar clientes:', error);
    return [];
  }
};
```

### **4. Hook React para Gestión de Personas**

```jsx
// hooks/usePersons.js
import { useState, useEffect } from 'react';

export const usePersons = (token) => {
  const [persons, setPersons] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadPersons = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/v1/persons/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Error al cargar personas');
      }

      const data = await response.json();
      setPersons(data);
    } catch (err) {
      setError(err.message);
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      loadPersons();
    }
  }, [token]);

  const getPersonById = (id) => {
    return persons.find(person => person.id === id);
  };

  const searchPersons = (searchTerm) => {
    if (!searchTerm) return persons;
    
    return persons.filter(person => 
      person.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      person.document_number.includes(searchTerm)
    );
  };

  return {
    persons,
    loading,
    error,
    loadPersons,
    getPersonById,
    searchPersons
  };
};

// Uso del hook
const SaleComponent = () => {
  const { persons, loading, getPersonById, searchPersons } = usePersons(authToken);
  
  // Usar personas en el componente...
};
```

### **5. Ejemplos de Uso en Diferentes Contextos**

#### **A. Venta a Granel:**
```javascript
const sellBulkProduct = async (productData, customerId, userId) => {
  const saleData = {
    bulk_conversion_id: productData.bulkConversionId,
    quantity: parseInt(productData.quantity),
    unit_price: parseFloat(productData.price),
    customer_id: customerId,  // UUID de persona seleccionada
    user_id: userId          // UUID del usuario logueado
  };

  const response = await fetch('/api/v1/products/sell-bulk/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(saleData)
  });

  return await response.json();
};
```

#### **B. Venta Normal:**
```javascript
const sellRegularProduct = async (productData, customerId, userId) => {
  const saleData = {
    customer_id: customerId,
    user_id: userId,
    items: productData.items,
    total: productData.total
  };

  // Implementar endpoint de venta normal aquí
  const response = await fetch('/api/v1/sales/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(saleData)
  });

  return await response.json();
};
```

## 🔄 Flujo Completo de Venta

### **1. Inicialización:**
```javascript
// 1. Cargar lista de personas (clientes)
const persons = await personService.getAllPersons();

// 2. Obtener usuario actual (vendedor)
const currentUser = await getCurrentUser();

// 3. Cargar productos disponibles
const products = await getProducts();
```

### **2. Selección:**
```javascript
// 1. Usuario selecciona cliente de la lista
const selectedCustomer = persons.find(p => p.id === selectedCustomerId);

// 2. Usuario selecciona productos
const selectedProducts = [...];

// 3. Calcular total
const total = calculateTotal(selectedProducts);
```

### **3. Procesamiento:**
```javascript
// 1. Validar datos
if (!selectedCustomerId || !selectedProducts.length) {
  throw new Error('Datos incompletos');
}

// 2. Procesar venta
const saleResult = await processSale({
  customerId: selectedCustomerId,
  userId: currentUser.id,
  products: selectedProducts,
  total: total
});

// 3. Mostrar confirmación
showSaleConfirmation(saleResult);
```

## ⚠️ Consideraciones Importantes

### **1. Autenticación:**
- Todos los endpoints requieren token de autenticación
- Verificar que el usuario tenga permisos de venta

### **2. Validación:**
- Siempre validar que se seleccione un cliente
- Verificar que los UUIDs sean válidos
- Confirmar stock disponible antes de procesar

### **3. Manejo de Errores:**
```javascript
const handleSaleError = (error) => {
  if (error.status === 404) {
    alert('Cliente no encontrado');
  } else if (error.status === 400) {
    alert('Datos de venta inválidos');
  } else if (error.status === 403) {
    alert('No tiene permisos para realizar ventas');
  } else {
    alert('Error inesperado en la venta');
  }
};
```

### **4. UX/UI Recomendaciones:**
- Mostrar información clara del cliente seleccionado
- Incluir buscador para facilitar selección de clientes
- Mostrar confirmación antes de procesar venta
- Mantener historial de ventas recientes

## 🎯 Campos Clave para Frontend

| Campo | Tipo | Descripción | Uso en Ventas |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | `customer_id` en ventas |
| `full_name` | String | Nombre completo | Mostrar en UI |
| `document_type` | String | Tipo documento (CC, CE, etc.) | Identificación |
| `document_number` | String | Número de documento | Identificación |

## 📱 Ejemplo de UI Completa

```jsx
const CompleteSaleInterface = () => {
  return (
    <div className="sale-interface">
      <header>
        <h1>🛒 Sistema de Ventas</h1>
      </header>
      
      <div className="sale-form">
        {/* Selector de Cliente */}
        <CustomerSelector onSelect={handleCustomerSelect} />
        
        {/* Productos */}
        <ProductSelector onProductAdd={handleProductAdd} />
        
        {/* Resumen */}
        <SaleSummary 
          customer={selectedCustomer}
          products={selectedProducts}
          total={total}
        />
        
        {/* Botones */}
        <div className="actions">
          <button onClick={processSale}>Procesar Venta</button>
          <button onClick={resetSale}>Cancelar</button>
        </div>
      </div>
    </div>
  );
};
```

Este documento proporciona todo lo necesario para implementar correctamente el sistema de personas en las ventas. ¿Necesitas que detalle algún aspecto específico?

## 🚀 NUEVO: Registro Rápido de Clientes

### **Componente de Registro de Cliente**

```jsx
import React, { useState } from 'react';

const QuickCustomerRegistration = ({ onCustomerCreated }) => {
  const [formData, setFormData] = useState({
    name: '',
    last_name: '',
    document_type: 'CC',
    document_number: '',
    phone: '',
    email: '',
    address: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/v1/persons/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
          // ✅ NO REQUIERE Authorization - endpoint público
        },
        body: JSON.stringify(formData)
      });

      const result = await response.json();

      if (response.ok) {
        // Cliente creado exitosamente
        onCustomerCreated(result.person);
        // Resetear formulario
        setFormData({
          name: '',
          last_name: '',
          document_type: 'CC',
          document_number: '',
          phone: '',
          email: '',
          address: ''
        });
        alert('Cliente registrado exitosamente');
      } else {
        // Manejar errores (documento duplicado, email duplicado, etc.)
        setError(result.detail);
      }
    } catch (error) {
      setError('Error de conexión. Intenta nuevamente.');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="quick-registration">
      <h3>🆕 Registrar Nuevo Cliente</h3>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="form-row">
        <input
          type="text"
          placeholder="Nombre *"
          value={formData.name}
          onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
          required
        />
        <input
          type="text"
          placeholder="Apellido *"
          value={formData.last_name}
          onChange={(e) => setFormData(prev => ({ ...prev, last_name: e.target.value }))}
          required
        />
      </div>

      <div className="form-row">
        <select
          value={formData.document_type}
          onChange={(e) => setFormData(prev => ({ ...prev, document_type: e.target.value }))}
          required
        >
          <option value="CC">Cédula de Ciudadanía</option>
          <option value="CE">Cédula de Extranjería</option>
          <option value="TI">Tarjeta de Identidad</option>
          <option value="PP">Pasaporte</option>
          <option value="NIT">NIT</option>
        </select>
        <input
          type="text"
          placeholder="Número de documento *"
          value={formData.document_number}
          onChange={(e) => setFormData(prev => ({ ...prev, document_number: e.target.value }))}
          required
        />
      </div>

      <div className="form-row">
        <input
          type="tel"
          placeholder="Teléfono (opcional)"
          value={formData.phone}
          onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
        />
        <input
          type="email"
          placeholder="Email (opcional)"
          value={formData.email}
          onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
        />
      </div>

      <input
        type="text"
        placeholder="Dirección (opcional)"
        value={formData.address}
        onChange={(e) => setFormData(prev => ({ ...prev, address: e.target.value }))}
      />

      <button type="submit" disabled={loading}>
        {loading ? 'Registrando...' : 'Registrar Cliente'}
      </button>
    </form>
  );
};

export default QuickCustomerRegistration;
```

### **Integración en Sistema de Ventas**

```jsx
const SaleInterface = () => {
  const [showRegistration, setShowRegistration] = useState(false);
  const [customers, setCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);

  const handleCustomerCreated = (newCustomer) => {
    // Agregar cliente a la lista
    setCustomers(prev => [...prev, newCustomer]);
    // Seleccionarlo automáticamente
    setSelectedCustomer(newCustomer);
    // Ocultar formulario de registro
    setShowRegistration(false);
  };

  return (
    <div className="sale-interface">
      <div className="customer-section">
        <CustomerSelector 
          customers={customers}
          selectedCustomer={selectedCustomer}
          onCustomerSelect={setSelectedCustomer}
        />
        
        <button 
          onClick={() => setShowRegistration(!showRegistration)}
          className="toggle-registration"
        >
          {showRegistration ? 'Cancelar' : '➕ Nuevo Cliente'}
        </button>

        {showRegistration && (
          <QuickCustomerRegistration 
            onCustomerCreated={handleCustomerCreated}
          />
        )}
      </div>
      
      {/* Resto del interface de ventas */}
    </div>
  );
};
```

### **Servicio JavaScript para Personas**

```javascript
// services/personService.js
class PersonService {
  constructor(baseURL = '/api/v1') {
    this.baseURL = baseURL;
  }

  // ✅ Crear persona - NO requiere autenticación
  async createPerson(personData) {
    const response = await fetch(`${this.baseURL}/persons/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(personData)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al crear persona');
    }

    return response.json();
  }

  // Obtener todas las personas - requiere autenticación
  async getAllPersons(token, searchTerm = '') {
    const url = searchTerm 
      ? `${this.baseURL}/persons/?search=${encodeURIComponent(searchTerm)}`
      : `${this.baseURL}/persons/`;

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error('Error al obtener personas');
    }

    return response.json();
  }

  // Obtener persona por ID - requiere autenticación
  async getPersonById(token, personId) {
    const response = await fetch(`${this.baseURL}/persons/${personId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error('Persona no encontrada');
    }

    return response.json();
  }
}

export default new PersonService();
```

### **Ejemplo de Uso Completo**

```javascript
// Registrar nuevo cliente durante venta
const registerAndSelectCustomer = async (customerData) => {
  try {
    const result = await PersonService.createPerson(customerData);
    
    // Cliente creado exitosamente
    console.log('Nuevo cliente:', result.person);
    
    // Seleccionar automáticamente para la venta
    setSelectedCustomerId(result.person.id);
    
    // Mostrar mensaje de éxito
    showSuccessMessage(`Cliente ${result.person.full_name} registrado exitosamente`);
    
  } catch (error) {
    // Manejar errores específicos
    if (error.message.includes('Ya existe una persona con')) {
      showErrorMessage('Este documento ya está registrado');
    } else if (error.message.includes('email')) {
      showErrorMessage('Este email ya está en uso');
    } else {
      showErrorMessage('Error al registrar cliente');
    }
  }
};

// Buscar clientes existentes
const searchCustomers = async (searchTerm) => {
  try {
    const customers = await PersonService.getAllPersons(token, searchTerm);
    setCustomerList(customers);
  } catch (error) {
    console.error('Error al buscar clientes:', error);
  }
};
```

## 🎯 Ventajas del Nuevo Sistema

1. **✅ Registro rápido**: No requiere autenticación
2. **🔒 Validaciones automáticas**: Documentos y emails únicos
3. **🔍 Búsqueda integrada**: Por nombre, documento o email
4. **⚡ Flujo optimizado**: Registrar y seleccionar en una sola acción
5. **📱 Responsive**: Funciona en todos los dispositivos

---

**🚀 ¡Sistema de personas completo y listo para implementar!**