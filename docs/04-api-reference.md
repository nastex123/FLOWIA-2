# 04 — Referencia de la API REST de FlowMind AI

La API REST de **FlowMind AI** expone endpoints para ingesta de documentos, consulta de extracciones, gestión de esquemas canónicos, normalización asistida, autenticación, reglas de automatización y webhooks salientes.

* **Base URL en desarrollo:** `http://127.0.0.1:8000`
* **Swagger UI interactivo:** `http://127.0.0.1:8000/docs`
* **Cabecera de Tenant:** `X-Organization-Id: <org_id>` (por defecto `default-org`).
* **Autenticación (requerida en todo `/api/v1` salvo `auth/login` y `auth/register`):**
  * `Authorization: Bearer <jwt>` (obtenido en `POST /api/v1/auth/login`), o
  * `X-API-Key: <fm_...>` para integraciones desatendidas.

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
    "ai_engine": "pure_libraries_local",
    "auth": "jwt_rbac_api_keys",
    "automation": "rules_webhooks"
  }
  ```

---

## 2. Autenticación y API Keys

### `POST /api/v1/auth/register`
Registra un usuario nuevo. Si no existe la organización indicada (o se especifica un nombre nuevo), se crea y el usuario pasa a ser **admin** de ella.

* **Payload JSON:**
  ```json
  {
    "email": "contabilidad@acme.com",
    "password": "clave-segura",
    "name": "Ana Pérez",
    "organization_id": "acme-org"
  }
  ```
* **Respuesta 200 OK:** `TokenResponse` (igual que login).

### `POST /api/v1/auth/login`
Autentica al usuario y devuelve el JWT.

* **Payload JSON:**
  ```json
  { "email": "admin@flowmind.local", "password": "admin123" }
  ```
* **Respuesta 200 OK:**
  ```json
  {
    "access_token": "<jwt>",
    "token_type": "bearer",
    "expires_in_minutes": 1440,
    "user": {
      "id": "2d7eb5e5-...",
      "email": "admin@flowmind.local",
      "role": "admin",
      "is_active": true,
      "created_at": "2026-08-16T04:41:49.597271"
    }
  }
  ```

### `GET /api/v1/auth/me`
Devuelve el usuario autenticado y sus organizaciones (para el selector multi-tenant).

* **Respuesta 200 OK:**
  ```json
  {
    "user": { "id": "...", "email": "admin@flowmind.local", "role": "admin", "is_active": true, "created_at": "..." },
    "default_organization": { "id": "default-org", "name": "Organización Principal" },
    "organizations": [ { "id": "default-org", "name": "Organización Principal" } ]
  }
  ```

### `GET /api/v1/auth/api-keys` *(admin/member)*
Lista las API Keys de la organización. Cada clave solo devuelve `prefix`, nunca el secreto.

### `POST /api/v1/auth/api-keys` *(admin/member)*
Crea una API Key. El valor en claro (prefijo `fm_`) **solo se muestra una vez**.

* **Payload JSON:** `{ "name": "Integración ERP Contabilidad", "expires_at": null }`
* **Respuesta 200 OK:** `{ "id": "...", "name": "...", "prefix": "fm_q3PSywH", "key": "fm_q3PSywH...", "is_active": true, ... }`

### `DELETE /api/v1/auth/api-keys/{key_id}` *(admin/member)*
Revoca una API Key (la desactiva).

---

## 3. Ingesta y Documentos

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

## 4. Esquemas de Datos (CRUD)

### `GET /api/v1/schemas`
Lista todas las definiciones de esquemas accesibles (estándar y personalizados).

### `POST /api/v1/schemas`
Crea un nuevo esquema canónico. *(admin/member)*

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
Elimina un esquema personalizado. *(admin/member)*

---

## 5. Mapeo y Normalización

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

*Nota:* al completar la normalización se evalúan automáticamente las reglas de automatización activas del evento `normalization_completed` y se disparan los webhooks que coincidan.

---

## 6. Reglas de Automatización (CRUD) *(admin)*

### `GET /api/v1/rules`
Lista las reglas de automatización de la organización.

### `POST /api/v1/rules`
Crea una regla. Se evalúa de forma determinista al completar extracción o normalización.

* **Payload JSON:**
  ```json
  {
    "name": "Alertar si total > 5.000€",
    "description": "Enviar aviso al ERP de facturas de importe elevado",
    "document_type": "invoice",
    "event": "extraction_completed",
    "field": "total_amount",
    "operator": "gt",
    "value": 5000,
    "webhook_ids": ["97378e6a-..."],
    "enabled": true
  }
  ```
* **Operadores:** `gt`, `lt`, `gte`, `lte`, `eq`, `neq`, `contains`, `is_empty`, `not_empty`.
* **Eventos:** `extraction_completed`, `normalization_completed`.

### `GET /api/v1/rules/{rule_id}`
Obtiene una regla por id.

### `PUT /api/v1/rules/{rule_id}`
Actualiza una regla (mismos campos que la creación).

### `DELETE /api/v1/rules/{rule_id}`
Elimina una regla.

### `POST /api/v1/rules/{rule_id}/evaluate?document_id={id}`
Evalúa la regla (dry-run) contra un documento ya procesado sin disparar webhooks.

* **Respuesta 200 OK:**
  ```json
  { "matched": true, "matched_value": 5240.5, "matched_rows": 1 }
  ```

---

## 7. Webhooks Salientes (CRUD) *(admin)*

### `GET /api/v1/webhooks`
Lista los webhooks configurados (sin secretos, solo `has_secret`).

### `POST /api/v1/webhooks`
Registra un endpoint saliente.

* **Payload JSON:**
  ```json
  {
    "name": "ERP Contabilidad",
    "url": "https://erp.example.com/webhook",
    "secret": "clave-hmac",
    "headers": { "X-Tenant": "acme" },
    "active": true
  }
  ```
  Si se indica `secret`, cada envío incluye la cabecera `X-Webhook-Signature: sha256=<hmac-hex>` del cuerpo.

### `GET /api/v1/webhooks/{webhook_id}`
Obtiene un webhook por id.

### `PUT /api/v1/webhooks/{webhook_id}`
Actualiza un webhook (mismos campos que la creación).

### `DELETE /api/v1/webhooks/{webhook_id}`
Elimina un webhook.

### `POST /api/v1/webhooks/{webhook_id}/test`
Envía un ping de prueba (`event: "webhook.test"`) y persiste la entrega en el registro de auditoría.

* **Respuesta 200 OK:**
  ```json
  { "status": "success", "http_status": 200, "duration_ms": 312 }
  ```

### `GET /api/v1/webhooks/deliveries`
Lista el registro de auditoría de entregas de la organización.

### `GET /api/v1/webhooks/{webhook_id}/deliveries`
Lista las entregas de un webhook concreto.

* **Campos por entrega:** `webhook_id`, `rule_id`, `document_id`, `event`, `url`, `status` (`success`/`failed`), `http_status`, `error_message`, `duration_ms`, `created_at`.
