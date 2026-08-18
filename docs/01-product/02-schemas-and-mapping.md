# Esquemas Canónicos y Mapeo Visual de Columnas

Este documento describe la arquitectura, algoritmos y uso del **Motor de Esquemas Canónicos y Mapeo Visual de Columnas** de **FlowMind AI**.

---

## 1. Problema de Negocio que Resuelve

En cadenas de suministro y procesos administrativos, diferentes proveedores, sucursales y clientes envían información tabular en hojas de cálculo con cabeceras heterogéneas:
* Proveedor A: `Cod_Art`, `Descripcion`, `PVP (€)`, `F_Emision`
* Proveedor B: `SKU`, `Product_Name`, `Unit_Cost`, `Order_Date`
* Proveedor C: `Referencia`, `Articulo`, `Precio`, `Fecha`

El **Motor de Esquemas de FlowMind AI** permite definir esquemas destino canónicos estándar y mapear automáticamente cualquier estructura de entrada hacia el formato estructurado de la empresa.

---

## 2. Estructura de un Esquema Canónico (`SchemaDefinition`)

Cada esquema define un conjunto de campos tipados:

```json
{
  "name": "Control de Inventario y Stock",
  "document_type": "inventory",
  "fields": [
    {
      "name": "sku",
      "label": "Código SKU / Referencia",
      "data_type": "string",
      "required": true,
      "aliases": ["sku", "ref", "referencia", "codigo", "codigo_articulo", "item_code"]
    },
    {
      "name": "stock_units",
      "label": "Stock Actual (Unidades)",
      "data_type": "number",
      "required": true,
      "aliases": ["stock", "stock_actual", "existencias", "unidades", "cantidad", "qty"]
    },
    {
      "name": "unit_cost",
      "label": "Coste Unitario (€)",
      "data_type": "number",
      "required": false,
      "aliases": ["coste_unitario", "coste", "precio_coste", "precio_unitario", "price"]
    }
  ]
}
```

---

## 3. Algoritmo de Auto-Mapeo Difuso (`rapidfuzz`)

El servicio `SchemaNormalizer` implementa un algoritmo de emparejamiento voraz por máxima afinidad (*Greedy Maximum Weight Assignment*):
1. **Matriz de Similitud:** Se evalúa cada columna origen contra todos los candidatos del campo destino (`name`, `label` y lista de `aliases`).
2. **Puntuación de Coincidencia:**
   - Coincidencia exacta de texto: Puntuación `1.0`.
   - Coincidencia difusa (`fuzz.token_sort_ratio`): Puntuación `ratio / 100`.
   - Solapamiento de subcadenas: Bonificación proporcional a la longitud compartida.
3. **Asignación Óptima:** Se ordenan los pares por puntuación descendente y se asignan evitando que una misma columna se use para múltiples campos incompatibles.

---

## 4. Normalización y Tipado de Datos

| Tipo (`data_type`) | Entrada Ejemplo | Salida Normalizada | Comportamiento |
| :--- | :--- | :--- | :--- |
| **`number`** | `" 1.250,50 € "` | `1250.50` (float) | Elimina símbolos de divisa (`€`, `$`, `USD`), espacios y convierte coma decimal europea. |
| **`date`** | `"18/06/2024"` | `"2024-06-18"` (ISO) | Soporta formatos `DD/MM/YYYY`, `YYYY-MM-DD`, `DD-MM-YYYY` y estandariza a ISO 8601. |
| **`boolean`** | `"Sí"`, `"1"`, `"True"` | `true` (bool) | Mapea variantes en español e inglés a booleanos nativos. |
| **`string`** | `"=CMD|' /C calc'"` | `"'=CMD|' /C calc'"` | Sanitiza inyecciones de fórmulas CSV anteponiendo comilla simple. |
