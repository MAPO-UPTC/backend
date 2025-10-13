# 📊 Diagrama: Proceso de Conversión a Granel

## 🔄 Flujo Visual del Proceso

```
┌─────────────────────────────────────────────────────────────────┐
│                    INVENTARIO INICIAL                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Producto: Arroz Diana - Paquete x 500g                        │
│  Stock Empaquetado: 10 paquetes                                 │
│  Stock a Granel: 0g                                             │
│                                                                  │
│  📦 📦 📦 📦 📦 📦 📦 📦 📦 📦                                   │
│  (10 paquetes cerrados)                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ Usuario hace clic en
                            │ "Abrir para Granel"
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MODAL DE CONVERSIÓN                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📦➡️🌾 Abrir Bulto para Granel                                 │
│                                                                  │
│  Producto: Arroz Diana                                          │
│  Presentación: Paquete x 500g                                   │
│  Paquetes disponibles: 10                                       │
│                                                                  │
│  ┌──────────────────────────────────────────────┐              │
│  │ Presentación Granel: [Granel (gramos)    ▼] │              │
│  └──────────────────────────────────────────────┘              │
│                                                                  │
│  ┌──────────────────────────────────────────────┐              │
│  │ Cantidad en Paquete: [500                  ] │              │
│  └──────────────────────────────────────────────┘              │
│                                                                  │
│  [Cancelar]  [Abrir Bulto]                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ Usuario confirma
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              REQUEST AL BACKEND                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  POST /products/open-bulk/                                      │
│                                                                  │
│  {                                                              │
│    "source_lot_detail_id": "uuid-lote",                        │
│    "target_presentation_id": "uuid-granel",                    │
│    "quantity": 500                                             │
│  }                                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ Backend procesa
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              OPERACIONES EN BASE DE DATOS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1️⃣  UPDATE lot_detail                                         │
│      SET quantity_available = quantity_available - 1            │
│      WHERE id = source_lot_detail_id                            │
│                                                                  │
│      (10 paquetes → 9 paquetes)                                 │
│                                                                  │
│  2️⃣  INSERT INTO bulk_conversion                               │
│      (source_lot_detail_id, target_presentation_id,             │
│       converted_quantity, remaining_bulk, status)               │
│      VALUES (uuid, uuid, 500, 500, 'ACTIVE')                    │
│                                                                  │
│      (Se crea registro de 500g a granel)                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ Backend responde
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   RESPUESTA EXITOSA                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  {                                                              │
│    "message": "Bulto abierto exitosamente",                    │
│    "bulk_conversion_id": "uuid-conversion",                    │
│    "converted_quantity": 500,                                  │
│    "remaining_bulk": 500,                                      │
│    "status": "ACTIVE"                                          │
│  }                                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ Frontend actualiza
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                 INVENTARIO ACTUALIZADO                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Producto: Arroz Diana - Paquete x 500g                        │
│  Stock Empaquetado: 9 paquetes                                  │
│  Stock a Granel: 500g disponibles                               │
│                                                                  │
│  📦 📦 📦 📦 📦 📦 📦 📦 📦  🌾                                  │
│  (9 paquetes cerrados)      (500g sueltos)                     │
│                                                                  │
│  ✅ Ahora se puede vender:                                      │
│     - Por paquetes completos (500g)                             │
│     - A granel (100g, 250g, etc.)                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔁 Ciclo de Vida de una Conversión

```
┌──────────────┐
│   CREACIÓN   │  ← POST /products/open-bulk/
└──────┬───────┘
       │
       │ status: "ACTIVE"
       │ remaining_bulk: 500
       │
       ▼
┌──────────────┐
│   ACTIVA     │  ← Se puede vender a granel
└──────┬───────┘    GET /products/bulk-stock/
       │
       │ Cliente compra 100g
       │ remaining_bulk: 400
       │
       ▼
┌──────────────┐
│   ACTIVA     │  ← Aún hay stock disponible
└──────┬───────┘    remaining_bulk: 400
       │
       │ Cliente compra 400g
       │ remaining_bulk: 0
       │
       ▼
┌──────────────┐
│  COMPLETADA  │  ← Se vendió todo el granel
└──────────────┘    status: "COMPLETED"
```

---

## 📊 Diagrama de Estados

```
┌─────────────────────────────────────────────────────────────┐
│                    BULK CONVERSION                           │
│                                                              │
│  ┌────────────┐   Vender    ┌────────────┐   Vender todo  │
│  │   ACTIVE   │──────────→  │   ACTIVE   │──────────────→ │
│  │ (500g)     │   100g      │ (400g)     │                │
│  └────────────┘             └────────────┘                │
│       │                            │                        │
│       │                            │                        │
│       ▼                            ▼                        │
│  remaining_bulk                remaining_bulk              │
│  disminuye                     llega a 0                   │
│                                     │                        │
│                                     ▼                        │
│                            ┌──────────────┐                │
│                            │  COMPLETED   │                │
│                            │   (0g)       │                │
│                            └──────────────┘                │
│                                                              │
│  Opcional: Cancelar conversión                              │
│  ┌────────────┐   Cancelar  ┌──────────────┐              │
│  │   ACTIVE   │───────────→ │  CANCELLED   │              │
│  │ (cualquier)│             │              │              │
│  └────────────┘             └──────────────┘              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Sistema FIFO (First In, First Out)

```
Escenario: Se abren 3 paquetes en diferentes momentos

┌──────────────────────────────────────────────────────────────┐
│                   TIMELINE                                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  DÍA 1: Se abre Paquete A                                   │
│  ┌────────────────────────────────────────┐                 │
│  │ Bulk Conversion #1                     │                 │
│  │ Fecha: 2025-10-01                      │                 │
│  │ Cantidad: 500g                         │                 │
│  │ Restante: 500g                         │                 │
│  └────────────────────────────────────────┘                 │
│                                                               │
│  DÍA 3: Se abre Paquete B                                   │
│  ┌────────────────────────────────────────┐                 │
│  │ Bulk Conversion #2                     │                 │
│  │ Fecha: 2025-10-03                      │                 │
│  │ Cantidad: 500g                         │                 │
│  │ Restante: 500g                         │                 │
│  └────────────────────────────────────────┘                 │
│                                                               │
│  DÍA 5: Se abre Paquete C                                   │
│  ┌────────────────────────────────────────┐                 │
│  │ Bulk Conversion #3                     │                 │
│  │ Fecha: 2025-10-05                      │                 │
│  │ Cantidad: 500g                         │                 │
│  │ Restante: 500g                         │                 │
│  └────────────────────────────────────────┘                 │
│                                                               │
└──────────────────────────────────────────────────────────────┘

Cliente quiere comprar 800g a granel

┌──────────────────────────────────────────────────────────────┐
│              SISTEMA APLICA FIFO                              │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Toma TODO del Bulk Conversion #1 (más antiguo)          │
│     → 500g del Paquete A                                     │
│     → Restante: 0g (COMPLETED)                              │
│                                                               │
│  2. Necesita 300g más (800 - 500 = 300)                     │
│     Toma del Bulk Conversion #2 (siguiente más antiguo)     │
│     → 300g del Paquete B                                     │
│     → Restante: 200g (ACTIVE)                               │
│                                                               │
│  3. No toca el Bulk Conversion #3                           │
│     → 500g del Paquete C                                     │
│     → Restante: 500g (ACTIVE)                               │
│                                                               │
└──────────────────────────────────────────────────────────────┘

Resultado Final:
  ✅ Cliente recibe 800g
  ✅ Se usó primero el paquete más antiguo (FIFO)
  ✅ Stock a granel actualizado automáticamente
```

---

## 📱 Interfaz de Usuario - Wireframe

```
┌────────────────────────────────────────────────────────────┐
│  MAPO - Gestión de Inventario                              │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Producto: Arroz Diana                              │   │
│  │ Presentación: Paquete x 500g                       │   │
│  ├────────────────────────────────────────────────────┤   │
│  │                                                     │   │
│  │  📦 Stock Empaquetado:   9 paquetes               │   │
│  │  🌾 Stock a Granel:      500g disponibles         │   │
│  │                                                     │   │
│  │  ┌──────────────────────────────────────────┐     │   │
│  │  │  [📦➡️🌾 Abrir para Granel]              │     │   │
│  │  └──────────────────────────────────────────┘     │   │
│  │                                                     │   │
│  │  Historial de Conversiones:                       │   │
│  │  ┌─────────────────────────────────────────┐      │   │
│  │  │ 2025-10-13 10:30                        │      │   │
│  │  │ Abierto: 500g | Vendido: 150g          │      │   │
│  │  │ Disponible: 350g                        │      │   │
│  │  │ Estado: 🟢 ACTIVO                       │      │   │
│  │  └─────────────────────────────────────────┘      │   │
│  │                                                     │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## 🎯 Casos de Uso Visualizados

### Caso 1: Cliente quiere 300g pero solo hay paquetes de 500g

```
ANTES:
┌─────────────────────┐
│ Stock: 10 paquetes  │
│ No venta a granel   │
│ ❌ No puede vender  │
│    300g             │
└─────────────────────┘

Usuario abre 1 bulto
         ↓

DESPUÉS:
┌─────────────────────┐
│ Stock: 9 paquetes   │
│ Granel: 500g        │
│ ✅ Puede vender     │
│    300g (sobran 200)│
└─────────────────────┘
```

### Caso 2: Optimizar stock próximo a vencer

```
Tienes 2 paquetes que vencen en 3 días

ESTRATEGIA:
1. Abrir ambos paquetes (1000g total)
2. Ofrecer descuento por granel
3. Vender rápido antes del vencimiento

┌──────────────────────────────────┐
│ 📦📦 → 🌾🌾 (1000g)              │
│                                  │
│ Descuento: 10% por granel        │
│ Resultado: Vendido en 2 días     │
│ ✅ Evita desperdicio             │
└──────────────────────────────────┘
```

---

**Guía visual completa! 🎨**

Ver documentación técnica en: `docs/BULK_CONVERSION_GUIDE.md`
