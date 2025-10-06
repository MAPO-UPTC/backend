# 🏗️ Arquitectura y Tipos TypeScript para Frontend

## 📝 Definiciones de Tipos

### Tipos Base
```typescript
// Tipos de identificadores
type UUID = string;
type Timestamp = string; // ISO 8601 format

// Respuesta de autenticación
interface AuthResponse {
  access_token: string;
  token_type: "Bearer";
  user: User;
}

interface User {
  id: UUID;
  uid: string;
  email: string;
  person: Person;
  roles?: Role[];
}

interface Person {
  id: UUID;
  first_name: string;
  last_name: string;
  phone?: string;
  email?: string;
  document_type?: string;
  document_number?: string;
}

interface Role {
  id: number;
  name: string;
  description?: string;
}
```

### Tipos de Inventario
```typescript
interface Category {
  id: UUID;
  name: string;
  description?: string;
}

interface Product {
  id: UUID;
  name: string;
  description?: string;
  category_id: UUID;
  category?: Category;
  presentations: ProductPresentation[];
}

interface ProductPresentation {
  id: UUID;
  product_id: UUID;
  presentation_name: string;
  unit_of_measure: string;
  quantity_per_unit: number;
  barcode?: string;
  current_stock?: number;
  product?: Product;
}

interface Supplier {
  id: UUID;
  person_id: UUID;
  supplier_code: string;
  person: Person;
}

interface Lot {
  id: UUID;
  supplier_id: UUID;
  received_date: Timestamp;
  lot_code: string;
  status: "active" | "inactive" | "expired";
  supplier?: Supplier;
  details?: LotDetail[];
}

interface LotDetail {
  id: UUID;
  lot_id: UUID;
  presentation_id: UUID;
  quantity_received: number;
  quantity_available: number;
  unit_cost: number;
  expiration_date?: Timestamp;
  production_date?: Timestamp;
  presentation?: ProductPresentation;
}

interface StockInfo {
  presentation_id: UUID;
  available_stock: number;
  total_lots: number;
  next_expiration?: Timestamp;
}
```

### Tipos de Ventas
```typescript
interface SaleItem {
  presentation_id: UUID;
  quantity: number;
  unit_price: number;
}

interface SaleCreate {
  customer_id: UUID;
  status: "completed" | "pending" | "cancelled";
  items: SaleItem[];
}

interface Sale {
  id: UUID;
  sale_code: string;
  sale_date: Timestamp;
  customer_id: UUID;
  user_id: UUID;
  total: number;
  status: "completed" | "pending" | "cancelled";
  items: SaleDetail[];
}

interface SaleDetail {
  id: UUID;
  sale_id: UUID;
  presentation_id: UUID;
  lot_detail_id?: UUID;
  bulk_conversion_id?: UUID;
  quantity: number;
  unit_price: number;
  line_total: number;
}

interface SalesReportFilter {
  start_date?: Timestamp;
  end_date?: Timestamp;
  customer_id?: UUID;
  user_id?: UUID;
}

interface ProductSalesStats {
  presentation_id: UUID;
  presentation_name: string;
  total_sold: number;
  total_revenue: number;
}

interface BestSellingProductsReport {
  best_selling_products: ProductSalesStats[];
  generated_at: Timestamp;
}

interface DailySalesSummary {
  date: Timestamp;
  total_sales: number;
  total_revenue: number;
  total_items_sold: number;
  average_sale_value: number;
}
```

### Tipos de Estado de la Aplicación
```typescript
interface AppState {
  auth: AuthState;
  cart: CartState;
  inventory: InventoryState;
  sales: SalesState;
  ui: UIState;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
}

interface CartState {
  items: CartItem[];
  customer: Person | null;
  total: number;
}

interface CartItem {
  presentation: ProductPresentation;
  quantity: number;
  unit_price: number;
  line_total: number;
  max_available?: number;
}

interface InventoryState {
  categories: Category[];
  products: Product[];
  currentCategory: UUID | null;
  loading: boolean;
}

interface SalesState {
  sales: Sale[];
  currentSale: Sale | null;
  reports: {
    bestSelling: ProductSalesStats[];
    dailySummary: DailySalesSummary[];
  };
  loading: boolean;
}

interface UIState {
  notifications: Notification[];
  modals: {
    customerSelector: boolean;
    productDetails: boolean;
  };
  loading: {
    [key: string]: boolean;
  };
}

interface Notification {
  id: string;
  type: "success" | "error" | "warning" | "info";
  title: string;
  message: string;
  timestamp: Timestamp;
}
```

---

## 🔧 API Client TypeScript

```typescript
class MAPOAPIClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('token');
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const config: RequestInit = {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      if (response.status === 401) {
        this.handleAuthError();
        throw new Error('Authentication required');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  private handleAuthError(): void {
    this.token = null;
    localStorage.removeItem('token');
    // Aquí puedes agregar lógica para redirigir al login
    window.dispatchEvent(new CustomEvent('auth:logout'));
  }

  // Auth endpoints
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    this.token = response.access_token;
    localStorage.setItem('token', this.token);
    return response;
  }

  async logout(): Promise<void> {
    this.token = null;
    localStorage.removeItem('token');
  }

  // Inventory endpoints
  async getCategories(): Promise<Category[]> {
    return this.request<Category[]>('/inventory/categories');
  }

  async getProductsByCategory(categoryId: UUID): Promise<Product[]> {
    return this.request<Product[]>(`/inventory/categories/${categoryId}/products`);
  }

  async getStock(presentationId: UUID): Promise<StockInfo> {
    return this.request<StockInfo>(`/inventory/presentations/${presentationId}/stock`);
  }

  async createLot(lotData: {
    supplier_id: UUID;
    received_date: Timestamp;
    lot_code: string;
    status: string;
  }): Promise<Lot> {
    return this.request<Lot>('/inventory/lots', {
      method: 'POST',
      body: JSON.stringify(lotData),
    });
  }

  async addProductsToLot(
    lotId: UUID,
    productData: {
      presentation_id: UUID;
      quantity_received: number;
      unit_cost: number;
      expiration_date?: Timestamp;
      production_date?: Timestamp;
    }
  ): Promise<LotDetail> {
    return this.request<LotDetail>(`/inventory/lots/${lotId}/products`, {
      method: 'POST',
      body: JSON.stringify(productData),
    });
  }

  // Sales endpoints
  async createSale(saleData: SaleCreate): Promise<Sale> {
    return this.request<Sale>('/sales/', {
      method: 'POST',
      body: JSON.stringify(saleData),
    });
  }

  async getSales(skip: number = 0, limit: number = 50): Promise<Sale[]> {
    return this.request<Sale[]>(`/sales/?skip=${skip}&limit=${limit}`);
  }

  async getSaleById(saleId: UUID): Promise<Sale> {
    return this.request<Sale>(`/sales/${saleId}`);
  }

  async getSaleByCode(saleCode: string): Promise<Sale> {
    return this.request<Sale>(`/sales/code/${saleCode}`);
  }

  async getBestSellingProducts(limit: number = 10): Promise<BestSellingProductsReport> {
    return this.request<BestSellingProductsReport>(`/sales/reports/best-products?limit=${limit}`);
  }

  async getSalesReport(filters: SalesReportFilter): Promise<any> {
    const params = new URLSearchParams();
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.customer_id) params.append('customer_id', filters.customer_id);
    if (filters.user_id) params.append('user_id', filters.user_id);

    return this.request<any>(`/sales/reports/summary?${params.toString()}`);
  }

  async getDailySummary(date: Timestamp): Promise<DailySalesSummary> {
    return this.request<DailySalesSummary>(`/sales/reports/daily/${date}`);
  }
}
```

---

## 🎯 Store/State Management (React + Zustand ejemplo)

```typescript
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface MAPOStore extends AppState {
  // Auth actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  
  // Cart actions
  addToCart: (presentation: ProductPresentation, quantity: number, unitPrice: number) => void;
  removeFromCart: (presentationId: UUID) => void;
  updateCartQuantity: (presentationId: UUID, quantity: number) => void;
  clearCart: () => void;
  setCustomer: (customer: Person) => void;
  
  // Sales actions
  createSale: () => Promise<Sale>;
  loadSales: () => Promise<void>;
  
  // Inventory actions
  loadCategories: () => Promise<void>;
  loadProductsByCategory: (categoryId: UUID) => Promise<void>;
  checkStock: (presentationId: UUID) => Promise<StockInfo>;
  
  // UI actions
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  setLoading: (key: string, loading: boolean) => void;
}

const api = new MAPOAPIClient();

export const useMAPOStore = create<MAPOStore>()(
  devtools(
    (set, get) => ({
      // Initial state
      auth: {
        user: null,
        token: localStorage.getItem('token'),
        isAuthenticated: !!localStorage.getItem('token'),
        loading: false,
      },
      cart: {
        items: [],
        customer: null,
        total: 0,
      },
      inventory: {
        categories: [],
        products: [],
        currentCategory: null,
        loading: false,
      },
      sales: {
        sales: [],
        currentSale: null,
        reports: {
          bestSelling: [],
          dailySummary: [],
        },
        loading: false,
      },
      ui: {
        notifications: [],
        modals: {
          customerSelector: false,
          productDetails: false,
        },
        loading: {},
      },

      // Auth actions
      login: async (email: string, password: string) => {
        set((state) => ({
          auth: { ...state.auth, loading: true },
        }));

        try {
          const response = await api.login(email, password);
          set((state) => ({
            auth: {
              ...state.auth,
              user: response.user,
              token: response.access_token,
              isAuthenticated: true,
              loading: false,
            },
          }));
        } catch (error) {
          set((state) => ({
            auth: { ...state.auth, loading: false },
          }));
          get().addNotification({
            type: 'error',
            title: 'Error de autenticación',
            message: error instanceof Error ? error.message : 'Error desconocido',
          });
          throw error;
        }
      },

      logout: () => {
        api.logout();
        set({
          auth: {
            user: null,
            token: null,
            isAuthenticated: false,
            loading: false,
          },
          cart: {
            items: [],
            customer: null,
            total: 0,
          },
        });
      },

      // Cart actions
      addToCart: (presentation, quantity, unitPrice) => {
        set((state) => {
          const existingItem = state.cart.items.find(
            item => item.presentation.id === presentation.id
          );

          let newItems: CartItem[];
          if (existingItem) {
            newItems = state.cart.items.map(item =>
              item.presentation.id === presentation.id
                ? { ...item, quantity: item.quantity + quantity, line_total: (item.quantity + quantity) * item.unit_price }
                : item
            );
          } else {
            newItems = [...state.cart.items, {
              presentation,
              quantity,
              unit_price: unitPrice,
              line_total: quantity * unitPrice,
            }];
          }

          const total = newItems.reduce((sum, item) => sum + item.line_total, 0);

          return {
            cart: {
              ...state.cart,
              items: newItems,
              total,
            },
          };
        });
      },

      removeFromCart: (presentationId) => {
        set((state) => {
          const newItems = state.cart.items.filter(
            item => item.presentation.id !== presentationId
          );
          const total = newItems.reduce((sum, item) => sum + item.line_total, 0);

          return {
            cart: {
              ...state.cart,
              items: newItems,
              total,
            },
          };
        });
      },

      updateCartQuantity: (presentationId, quantity) => {
        set((state) => {
          const newItems = state.cart.items.map(item =>
            item.presentation.id === presentationId
              ? { ...item, quantity, line_total: quantity * item.unit_price }
              : item
          );
          const total = newItems.reduce((sum, item) => sum + item.line_total, 0);

          return {
            cart: {
              ...state.cart,
              items: newItems,
              total,
            },
          };
        });
      },

      clearCart: () => {
        set((state) => ({
          cart: {
            ...state.cart,
            items: [],
            total: 0,
          },
        }));
      },

      setCustomer: (customer) => {
        set((state) => ({
          cart: {
            ...state.cart,
            customer,
          },
        }));
      },

      // Sales actions
      createSale: async () => {
        const { cart, auth } = get();
        
        if (!cart.customer || cart.items.length === 0) {
          throw new Error('Carrito vacío o cliente no seleccionado');
        }

        try {
          const saleData: SaleCreate = {
            customer_id: cart.customer.id,
            status: 'completed',
            items: cart.items.map(item => ({
              presentation_id: item.presentation.id,
              quantity: item.quantity,
              unit_price: item.unit_price,
            })),
          };

          const sale = await api.createSale(saleData);
          
          get().clearCart();
          get().addNotification({
            type: 'success',
            title: 'Venta procesada',
            message: `Venta ${sale.sale_code} creada exitosamente`,
          });

          return sale;
        } catch (error) {
          get().addNotification({
            type: 'error',
            title: 'Error al procesar venta',
            message: error instanceof Error ? error.message : 'Error desconocido',
          });
          throw error;
        }
      },

      loadSales: async () => {
        set((state) => ({
          sales: { ...state.sales, loading: true },
        }));

        try {
          const sales = await api.getSales();
          set((state) => ({
            sales: {
              ...state.sales,
              sales,
              loading: false,
            },
          }));
        } catch (error) {
          set((state) => ({
            sales: { ...state.sales, loading: false },
          }));
          throw error;
        }
      },

      // Inventory actions
      loadCategories: async () => {
        set((state) => ({
          inventory: { ...state.inventory, loading: true },
        }));

        try {
          const categories = await api.getCategories();
          set((state) => ({
            inventory: {
              ...state.inventory,
              categories,
              loading: false,
            },
          }));
        } catch (error) {
          set((state) => ({
            inventory: { ...state.inventory, loading: false },
          }));
          throw error;
        }
      },

      loadProductsByCategory: async (categoryId) => {
        set((state) => ({
          inventory: { ...state.inventory, loading: true, currentCategory: categoryId },
        }));

        try {
          const products = await api.getProductsByCategory(categoryId);
          set((state) => ({
            inventory: {
              ...state.inventory,
              products,
              loading: false,
            },
          }));
        } catch (error) {
          set((state) => ({
            inventory: { ...state.inventory, loading: false },
          }));
          throw error;
        }
      },

      checkStock: async (presentationId) => {
        return await api.getStock(presentationId);
      },

      // UI actions
      addNotification: (notification) => {
        const id = Math.random().toString(36).substring(7);
        const timestamp = new Date().toISOString();
        
        set((state) => ({
          ui: {
            ...state.ui,
            notifications: [
              ...state.ui.notifications,
              { ...notification, id, timestamp },
            ],
          },
        }));

        // Auto-remove after 5 seconds
        setTimeout(() => {
          get().removeNotification(id);
        }, 5000);
      },

      removeNotification: (id) => {
        set((state) => ({
          ui: {
            ...state.ui,
            notifications: state.ui.notifications.filter(n => n.id !== id),
          },
        }));
      },

      setLoading: (key, loading) => {
        set((state) => ({
          ui: {
            ...state.ui,
            loading: {
              ...state.ui.loading,
              [key]: loading,
            },
          },
        }));
      },
    }),
    {
      name: 'mapo-store',
    }
  )
);
```

---

## 🎨 Ejemplo de Hook Custom (React)

```typescript
// hooks/useSales.ts
import { useCallback } from 'react';
import { useMAPOStore } from '../store/mapoStore';

export const useSales = () => {
  const {
    sales,
    createSale,
    loadSales,
    cart,
    addToCart,
    removeFromCart,
    updateCartQuantity,
    clearCart,
    setCustomer,
    addNotification,
  } = useMAPOStore();

  const processSale = useCallback(async () => {
    try {
      if (!cart.customer) {
        addNotification({
          type: 'warning',
          title: 'Cliente requerido',
          message: 'Debe seleccionar un cliente antes de procesar la venta',
        });
        return null;
      }

      if (cart.items.length === 0) {
        addNotification({
          type: 'warning',
          title: 'Carrito vacío',
          message: 'Debe agregar productos al carrito',
        });
        return null;
      }

      const sale = await createSale();
      return sale;
    } catch (error) {
      console.error('Error processing sale:', error);
      return null;
    }
  }, [cart, createSale, addNotification]);

  const addProductToCart = useCallback(async (
    presentation: ProductPresentation,
    quantity: number,
    unitPrice: number
  ) => {
    try {
      // Verificar stock disponible
      const api = new MAPOAPIClient();
      const stockInfo = await api.getStock(presentation.id);

      const currentQuantityInCart = cart.items.find(
        item => item.presentation.id === presentation.id
      )?.quantity || 0;

      if (currentQuantityInCart + quantity > stockInfo.available_stock) {
        addNotification({
          type: 'warning',
          title: 'Stock insuficiente',
          message: `Solo hay ${stockInfo.available_stock} unidades disponibles`,
        });
        return false;
      }

      addToCart(presentation, quantity, unitPrice);
      return true;
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Error al verificar stock',
        message: 'No se pudo verificar la disponibilidad del producto',
      });
      return false;
    }
  }, [cart.items, addToCart, addNotification]);

  return {
    // State
    sales: sales.sales,
    loading: sales.loading,
    cart,
    
    // Actions
    processSale,
    loadSales,
    addProductToCart,
    removeFromCart,
    updateCartQuantity,
    clearCart,
    setCustomer,
  };
};
```

---

## 🚀 Uso en Componentes React

```tsx
// components/SalesCart.tsx
import React from 'react';
import { useSales } from '../hooks/useSales';

export const SalesCart: React.FC = () => {
  const {
    cart,
    processSale,
    removeFromCart,
    updateCartQuantity,
    clearCart,
  } = useSales();

  const handleProcessSale = async () => {
    const sale = await processSale();
    if (sale) {
      console.log('Sale processed:', sale.sale_code);
    }
  };

  return (
    <div className="sales-cart">
      <h3>Carrito de Ventas</h3>
      
      {cart.customer && (
        <div className="customer-info">
          <strong>Cliente:</strong> {cart.customer.first_name} {cart.customer.last_name}
        </div>
      )}

      <div className="cart-items">
        {cart.items.map((item) => (
          <div key={item.presentation.id} className="cart-item">
            <span>{item.presentation.presentation_name}</span>
            <input
              type="number"
              value={item.quantity}
              onChange={(e) => updateCartQuantity(item.presentation.id, parseInt(e.target.value))}
              min="1"
            />
            <span>${item.unit_price}</span>
            <span>${item.line_total.toFixed(2)}</span>
            <button onClick={() => removeFromCart(item.presentation.id)}>
              Eliminar
            </button>
          </div>
        ))}
      </div>

      <div className="cart-total">
        <strong>Total: ${cart.total.toFixed(2)}</strong>
      </div>

      <div className="cart-actions">
        <button onClick={clearCart}>Limpiar</button>
        <button 
          onClick={handleProcessSale}
          disabled={!cart.customer || cart.items.length === 0}
        >
          Procesar Venta
        </button>
      </div>
    </div>
  );
};
```

Esta arquitectura TypeScript te proporciona:

1. **Tipos seguros** en toda la aplicación
2. **API client** robusto con manejo de errores
3. **Estado centralizado** con Zustand
4. **Hooks personalizados** para lógica de negocio
5. **Componentes tipados** y reutilizables

¡Perfecto para una implementación frontend robusta y escalable! 🎯