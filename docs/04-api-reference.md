# 04 — Referencia de la API REST de FlowMind AI

La API REST de **FlowMind AI** expone endpoints para ingesta de documentos, consulta de extracciones, gestión de esquemas canónicos y normalización asistida.

* **Base URL en desarrollo:** `http://127.0.0.1:8000`
* **Swagger UI interactivo:** `http://127.0.0.1:8000/docs`
* **Cabecera de Tenant:** `X-Organization-Id: <org_id>` (por defecto `default-org`).

---

## 1. Sistema & Healthcheck

### `GET /health`
Comprueba el estado de los componentes locales y base de datos.

* **Respuesta 200 OK:**
  ```json
  {
    "status": "healthy",
    "app": "FlowMind AI",
    "environment": "development",
    "storage": "local",
    "database": "sqlite_async",
    "ai_engine": "pure_libraries_local"
  }
  ```

---

## 2. Ingesta y Documentos

### `POST /api/v1/documents/upload`
Sube un archivo Excel, CSV o PDF e inicia el procesamiento en segundo plano.

* **Content-Type:** `multipart/form-data`
* **Parámetros:** `file` (archivo binario).
* **Respuesta 202 Accepted:**
  ```json
  {
    "document_id": "8f8b8946-b6b8-4775-9b2f-981881775791",
    "organization_id": "default-org",
    "filename": "factura_suministros_2024.xlsx",
    "status": "pending",
    "message": "Document uploaded successfully and queued for local extraction."
  }
  ```

### `GET /api/v1/documents/{document_id}`
Obtiene el estado de procesamiento y los datos extraídos (campos normalizados y tablas).

* **Respuesta 200 OK:**
  ```json
  {
    "document_id": "8f8b8946-b6b8-4775-9b2f-981881775791",
    "organization_id": "default-org",
    "filename": "factura_suministros_2024.xlsx",
    "file_size_bytes": 6230,
    "status": "completed",
    "created_at": "2026-08-15T21:00:00.000000",
    "error_message": null,
    "extraction": {
      "document_type": "invoice",
      "confidence": 0.95,
      "fields": {
        "invoice_number": {
          "key": "invoice_number",
          "value": "F-2024-0982",
          "confidence": 0.95,
          "extractor_type": "rule_regex"
        }
      },
      "tables": [
        {
          "sheet_or_page": "Factura F-2024-0982",
          "headers": ["Referencia", "Descripción de Producto", "Cantidad", "Precio Unitario (€)", "Importe (€)"],
          "rows_count": 5,
          "records": [...]
        }
      ],
      "processing_time_ms": 42.5
    }
  }
  ```

### `GET /api/v1/documents`
Lista todos los documentos registrados para la organización autenticada.

---

## 3. Esquemas de Datos (CRUD)

### `GET /api/v1/schemas`
Lista todas las definiciones de esquemas accesibles (estándar y personalizados).

### `POST /api/v1/schemas`
Crea un nuevo esquema canónico.

* **Payload JSON:**
  ```json
  {
    "name": "Esquema Catálogo ERP",
    "description": "Estandarización de productos de almacén",
    "document_type": "inventory",
    "fields": [
      {
        "name": "sku",
        "label": "Código SKU",
        "data_type": "string",
        "required": true,
        "aliases": ["ref", "codigo", "cod_art"]
      },
      {
        "name": "price",
        "label": "Precio Venta (€)",
        "data_type": "number",
        "required": true,
        "aliases": ["pvp", "precio", "unit_price"]
      }
    ]
  }
  ```

### `DELETE /api/v1/schemas/{schema_id}`
Elimina un esquema personalizado.

---

## 4. Mapeo y Normalización

### `POST /api/v1/documents/{document_id}/auto-map?schema_id={schema_id}&table_index=0`
Calcula sugerencias de coincidencia difusa entre las columnas del documento y los campos del esquema.

* **Respuesta 200 OK:**
  ```json
  {
    "schema_id": "preset-inventory-std",
    "schema_name": "Control de Inventario y Stock",
    "available_source_columns": ["Cod_Articulo", "Descripcion_Producto", "Stock_Actual", "Coste_Unitario"],
    "mappings": [
      {
        "target_field": "sku",
        "target_label": "Código SKU / Referencia",
        "data_type": "string",
        "required": true,
        "suggested_source_column": "Cod_Articulo",
        "confidence": 1.0
      },
      {
        "target_field": "product_name",
        "target_label": "Descripción del Artículo",
        "data_type": "string",
        "required": true,
        "suggested_source_column": "Descripcion_Producto",
        "confidence": 0.95
      }
    ]
  }
  ```

### `POST /api/v1/documents/{document_id}/normalize`
Aplica el mapeo confirmado y genera la tabla normalizada con tipos de datos convertidos.

* **Payload JSON:**
  ```json
  {
    "schema_id": "preset-inventory-std",
    "table_index": 0,
    "column_mapping": {
      "sku": "Cod_Articulo",
      "product_name": "Descripcion_Producto",
      "stock_units": "Stock_Actual",
      "unit_cost": "Coste_Unitario"
    }
  }
  ```

* **Respuesta 200 OK:**
  ```json
  {
    "schema_id": "preset-inventory-std",
    "schema_name": "Control de Inventario y Stock",
    "total_records": 8,
    "headers": ["sku", "product_name", "stock_units", "unit_cost"],
    "records": [
      {
        "sku": "HW-SRV-01",
        "product_name": "Servidor ProLiant DL380 Gen10",
        "stock_units": 14,
        "unit_cost": 2100.50
      }
    ],
    "validation_errors": []
  }
  ```
