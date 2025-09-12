# 📸 Documentación: Endpoints de Productos con image_url

## ✅ Estado: IMPLEMENTADO Y FUNCIONANDO

Los endpoints de productos ahora soportan completamente el campo `image_url` para almacenar URLs de imágenes de productos.

## 🔗 Endpoints Disponibles

### 1. Crear Producto
```http
POST /products/
Authorization: Bearer {token}
Content-Type: application/json
```

**Requiere permisos**: `PRODUCTS.CREATE` (roles ADMIN o SUPERADMIN)

**Body con imagen:**
```json
{
  "name": "Producto con Imagen",
  "description": "Descripción del producto",
  "image_url": "https://example.com/imagen.jpg",
  "category_id": "uuid-opcional"
}
```

**Body sin imagen:**
```json
{
  "name": "Producto sin Imagen",
  "description": "Descripción del producto"
}
```

**Respuesta:**
```json
{
  "message": "Product created successfully",
  "product": {
    "id": "uuid-generado",
    "name": "Producto con Imagen",
    "description": "Descripción del producto",
    "category_id": null,
    "image_url": "https://example.com/imagen.jpg"
  }
}
```

### 2. Listar Productos
```http
GET /products/
```

**No requiere autenticación** (público)

**Respuesta:**
```json
[
  {
    "id": "uuid1",
    "name": "Producto 1",
    "description": "Descripción 1",
    "category_id": null,
    "image_url": "https://example.com/imagen1.jpg"
  },
  {
    "id": "uuid2", 
    "name": "Producto 2",
    "description": "Descripción 2",
    "category_id": null,
    "image_url": null
  }
]
```

### 3. Obtener Producto por ID
```http
GET /products/{product_id}
```

**No requiere autenticación** (público)

**Respuesta:**
```json
{
  "id": "uuid",
  "name": "Producto Específico",
  "description": "Descripción específica",
  "category_id": null,
  "image_url": "https://example.com/imagen-especifica.jpg"
}
```

### 4. Actualizar Producto
```http
PUT /products/{product_id}
Authorization: Bearer {token}
Content-Type: application/json
```

**Requiere permisos**: `PRODUCTS.UPDATE` (roles ADMIN o SUPERADMIN)

**Agregar imagen a producto existente:**
```json
{
  "image_url": "https://example.com/nueva-imagen.jpg"
}
```

**Cambiar imagen existente:**
```json
{
  "description": "Nueva descripción",
  "image_url": "https://example.com/imagen-actualizada.jpg"
}
```

**Quitar imagen (establecer como null):**
```json
{
  "image_url": null
}
```

**Respuesta:**
```json
{
  "message": "Product updated successfully",
  "product": {
    "id": "uuid",
    "name": "Producto Actualizado",
    "description": "Descripción actualizada",
    "category_id": null,
    "image_url": "https://example.com/imagen-actualizada.jpg"
  }
}
```

### 5. Eliminar Producto
```http
DELETE /products/{product_id}
Authorization: Bearer {token}
```

**Requiere permisos**: `PRODUCTS.DELETE` (rol SUPERADMIN únicamente)

## 🧪 Ejemplos de Prueba

### Ejemplo con cURL
```bash
# Login
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "testadmin@x.com", "password": "a123456"}'

# Crear producto con imagen
curl -X POST "http://localhost:8000/products/" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Producto Test",
    "description": "Producto de prueba con imagen",
    "image_url": "https://picsum.photos/300/200"
  }'
```

### Ejemplo con JavaScript/Fetch
```javascript
// Login
const loginResponse = await fetch('/users/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'testadmin@x.com',
    password: 'a123456'
  })
});

const { idToken } = await loginResponse.json();

// Crear producto con imagen
const productResponse = await fetch('/products/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${idToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Producto JavaScript',
    description: 'Producto creado desde JavaScript',
    image_url: 'https://via.placeholder.com/300x200'
  })
});

const newProduct = await productResponse.json();
console.log('Producto creado:', newProduct);
```

### Ejemplo con Python requests
```python
import requests

# Login
login_response = requests.post('http://localhost:8000/users/login', json={
    'email': 'testadmin@x.com',
    'password': 'a123456'
})

token = login_response.json()['idToken']
headers = {'Authorization': f'Bearer {token}'}

# Crear producto con imagen
product_data = {
    'name': 'Producto Python',
    'description': 'Producto creado desde Python',
    'image_url': 'https://httpbin.org/image/jpeg'
}

response = requests.post(
    'http://localhost:8000/products/', 
    json=product_data,
    headers=headers
)

print('Producto creado:', response.json())
```

## 📋 Esquemas de Datos

### ProductCreate
```typescript
interface ProductCreate {
  name: string;                    // Requerido
  description: string;             // Requerido
  category_id?: string | null;     // Opcional
  image_url?: string | null;       // Opcional - URL de la imagen
}
```

### ProductUpdate
```typescript
interface ProductUpdate {
  name?: string;                   // Opcional
  description?: string;            // Opcional
  category_id?: string | null;     // Opcional
  image_url?: string | null;       // Opcional - null para quitar imagen
}
```

### ProductResponse
```typescript
interface ProductResponse {
  id: string;                      // UUID del producto
  name: string;                    // Nombre del producto
  description: string;             // Descripción del producto
  category_id: string | null;      // ID de categoría o null
  image_url: string | null;        // URL de imagen o null
}
```

## ✅ Funcionalidades Validadas

- ✅ **Crear producto CON imagen**: URL se guarda correctamente
- ✅ **Crear producto SIN imagen**: Campo se establece como null
- ✅ **Listar productos**: Incluye image_url en todas las respuestas
- ✅ **Obtener por ID**: Incluye image_url en la respuesta
- ✅ **Actualizar - agregar imagen**: A producto sin imagen
- ✅ **Actualizar - cambiar imagen**: Cambiar URL existente
- ✅ **Actualizar - quitar imagen**: Establecer como null
- ✅ **Campo opcional**: Funciona correctamente con/sin imagen
- ✅ **Persistencia**: Datos se guardan correctamente en BD
- ✅ **Permisos**: Solo usuarios autorizados pueden crear/actualizar

## 🔒 Permisos Requeridos

| Acción | Endpoint | Permisos Necesarios | Roles Autorizados |
|--------|----------|-------------------|------------------|
| Crear producto | POST /products/ | PRODUCTS.CREATE | ADMIN, SUPERADMIN |
| Listar productos | GET /products/ | Ninguno | Público |
| Ver producto | GET /products/{id} | Ninguno | Público |
| Actualizar producto | PUT /products/{id} | PRODUCTS.UPDATE | ADMIN, SUPERADMIN |
| Eliminar producto | DELETE /products/{id} | PRODUCTS.DELETE | SUPERADMIN |

## 🎯 Casos de Uso

### Caso 1: E-commerce
```json
{
  "name": "Smartphone Samsung Galaxy",
  "description": "Teléfono inteligente de última generación",
  "image_url": "https://cdn.tienda.com/productos/samsung-galaxy-s24.jpg"
}
```

### Caso 2: Producto sin imagen (temporal)
```json
{
  "name": "Producto Nuevo",
  "description": "Imagen pendiente de subir"
  // image_url se omite - será null
}
```

### Caso 3: Actualizar imagen después
```json
{
  "image_url": "https://cdn.tienda.com/productos/imagen-final.jpg"
}
```

## 🚀 Próximos Pasos

Para el frontend, ahora puedes:

1. **Mostrar imágenes** de productos usando `product.image_url`
2. **Manejar productos sin imagen** con placeholder cuando `image_url` es null
3. **Subir imágenes** a un servicio de almacenamiento y enviar la URL
4. **Actualizar imágenes** enviando la nueva URL
5. **Quitar imágenes** enviando `image_url: null`

---

## 🎉 Estado Final

**El sistema de productos con image_url está COMPLETAMENTE IMPLEMENTADO y FUNCIONANDO correctamente.** ✅

Todos los endpoints manejan correctamente el campo `image_url` y las pruebas han validado su funcionamiento en todos los escenarios posibles.