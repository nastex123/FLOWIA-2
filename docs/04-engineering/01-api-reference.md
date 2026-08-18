# Especificación y Referencia de la API REST de FlowMind AI

La API REST de **FlowMind AI** expone endpoints para ingesta de documentos, consulta de extracciones, gestión de esquemas canónicos, normalización asistida, autenticación, reglas de automatización, webhooks salientes, motor de decisión y cumplimiento fiscal.

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
          "records": []
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

### `GET /api/v1/rules/{rule_id}`
Obtiene una regla por id.

### `PUT /api/v1/rules/{rule_id}`
Actualiza una regla.

### `DELETE /api/v1/rules/{rule_id}`
Elimina una regla.

---

## 7. Webhooks Salientes (CRUD) *(admin)*

### `GET /api/v1/webhooks`
Lista los webhooks configurados.

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

### `GET /api/v1/webhooks/{webhook_id}`
Obtiene un webhook por id.

### `DELETE /api/v1/webhooks/{webhook_id}`
Elimina un webhook.

### `POST /api/v1/webhooks/{webhook_id}/test`
Envía un ping de prueba (`event: "webhook.test"`).

### `GET /api/v1/webhooks/deliveries`
Lista el registro de auditoría de entregas de la organización.

---

## 8. Motor de Decisión Empresarial & Sentinel (`/api/v1/decision`)

### `POST /api/v1/decision/validate-math`
Recalcula deterministamente los importes de un documento (base imponible por línea, suma de bases, IVA por tramos, recargos, retenciones y gastos de envío).

### `POST /api/v1/decision/entities/resolve`
Unifica variantes de nombres de clientes o proveedores contra la base histórica usando puntuación ponderada multidimensional.

### `POST /api/v1/decision/sentinel-audit`
Ejecuta la batería de auditoría continua antifraude de FlowMind Sentinel (cambio de IBAN no autorizado, duplicados multidimensionales y Ley de Benford).

---

## 9. Motores Especializados de Negocio (`/api/v1/business`)

### `POST /api/v1/business/three-way-match`
Reconcilia líneas de Pedido de Compra (PO), Albarán de Entrega (GR) y Factura de Proveedor (INV).

### `POST /api/v1/business/norma43/parse`
Parsea un fichero bancario estándar español **Norma 43 / CSB 43** extrayendo saldos y movimientos.

### `POST /api/v1/business/payroll/split`
Desagrega un PDF consolidado de nóminas masivas en ficheros PDF individuales por empleado.

---

## 10. Cumplimiento Fiscal & Anonimización PII (`/api/v1/compliance`)

### `POST /api/v1/compliance/sii/generate-xml`
Genera el payload XML oficial para el **Suministro Inmediato de Información (SII)** de la AEAT.

### `POST /api/v1/compliance/verifactu/chain-hash`
Calcula el hash SHA-256 encadenado inmutable y la cadena de payload para código QR conforme a **Veri\*factu / TicketBAI**.

### `POST /api/v1/compliance/pii/redact`
Detecta y anonimiza información sensible (DNI/NIE, IBANs, correos, teléfonos).
