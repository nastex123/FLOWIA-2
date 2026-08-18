# TDD — Extractor, Validador y Reconciliador de Facturas y Comprobantes

**Tipo:** Technical Design Document (TDD)
**Estado:** `Planned` — describe el diseño acordado, aún **no implementado**.
**Referencias:** [Alineación de la tarea](../01-product/04-proyecto4-alineacion-tarea.md), [ADR-003](../09-decisions/ADR-003-desktop-first-ui.md), [División de trabajo](../08-operations/02-trabajo-equipo-proyecto4.md).

---

## 1. Objetivo y Alcance

Convertir FlowMind AI en un **extractor, validador y reconciliador de facturas y comprobantes**:

1. **Extracción:** los motores existentes ya extraen campos y tablas; este TDD añade un **modelo de dominio de factura estructurado**.
2. **Validación:** conectar los validadores deterministas existentes (matemático, Sentinel, entidades) al pipeline de procesamiento y **persistir sus hallazgos**.
3. **Revisión visual:** una **app de escritorio PySide6** (cliente del backend) donde el equipo revisa comprobantes, visualiza proveedor/ítems/impuestos/totales y detecta anomalías visualmente.
4. **Automatización:** **hot-folder → backend** con API Key para alimentar la base de datos automáticamente (persiste, valida y dispara reglas/webhooks).

**Fuera de alcance en esta iteración:** cruce a 3 vías (PO/GR/INV) con UI, conector IMAP, Workbench 4-Ojos completo, frontend web Next.js (queda deprecated).

---

## 2. Dominio: Factura Estructurada

### 2.1 Modelos Pydantic (`backend/app/domain/invoice_models.py` — NUEVO)

```python
class InvoiceLineItem(BaseModel):
    description: str
    quantity: float | None = None
    unit_price: float | None = None
    discount_pct: float | None = None
    tax_rate_pct: float | None = None
    line_total: float | None = None

class TaxBreakdownItem(BaseModel):
    tax_rate_pct: float
    taxable_base: float
    tax_quota: float

class StructuredInvoice(BaseModel):
    document_id: str
    invoice_number: str | None = None
    vendor_name: str | None = None
    vendor_tax_id: str | None = None
    customer_name: str | None = None
    customer_tax_id: str | None = None
    issue_date: date | None = None
    due_date: date | None = None
    currency: str = "EUR"
    items: list[InvoiceLineItem] = []
    tax_breakdown: list[TaxBreakdownItem] = []
    subtotal: float | None = None
    tax_total: float | None = None
    total_amount: float | None = None
    withholding_amount: float | None = None
    shipping_amount: float | None = None
```

### 2.2 Algoritmo del `InvoiceStructurizer` (`backend/app/services/invoice/structurizer.py` — NUEVO)

Entrada: `ExtractionResult` (campos `ExtractedField` + tablas `ExtractedTable`). Salida: `StructuredInvoice`.

1. **Campos de cabecera** desde las keys canónicas del `RuleExtractor` (`invoice_number`, `issue_date`, `due_date`, `tax_id`, `vendor_name`, `customer_name`, `subtotal`, `tax_amount`, `total_amount`, `currency`) más aliases de los presets de esquema.
2. **Ítems** desde la tabla que mejor corresponda a líneas de factura:
   - Se calcula la afinidad de cada cabecera de tabla contra los alias canónicos de columnas (descripción, cantidad, precio unitario, % IVA, importe de línea) con `rapidfuzz.fuzz.token_sort_ratio` (asignación voraz por máxima afinidad, umbral ≥ 0.85 auto).
   - Cada fila se convierte a `InvoiceLineItem` con normalización numérica reutilizando `SchemaNormalizer.normalize_value`.
3. **Desglose de IVA**:
   - Si la tabla tiene columna de tipo de IVA, se agrupan las líneas por `tax_rate_pct` y se calcula `taxable_base` y `tax_quota` sumadas.
   - Si no, se usan los campos extraídos `subtotal`/`tax_amount` como tramo único.
4. **Totales**: se prefieren los valores recalculados por el validador matemático (sección 3) frente a los impresos en el documento; el documento impreso queda como referencia en `detail_json` de los checks.

---

## 3. Pipeline Integrado de Validación

Modificación de `backend/app/services/pipeline.py`. Tras la clasificación, cuando `document_type == invoice`:

```text
[CLASIFICACIÓN: invoice]
   │
   ▼
[1. STRUCTURIZER] ────────> StructuredInvoice
   │
   ▼
[2. VALIDACIÓN MATEMÁTICA]> MathematicalDocumentValidator.validate_invoice(...)
   │                         (recalcula bases, IVA, retenciones, totales; genera OK/WARNING/CRITICAL)
   ▼
[3. FLOWMIND SENTINEL] ────> audit_document(...) con histórico REAL desde BD
   │                         (cambio de IBAN, duplicado por fingerprint, evasión de umbral)
   ▼
[4. RESOLUCIÓN DE ENTIDADES]> EntityResolutionEngine.resolve(...)
   │                         → entity_id canónico; upsert entity_record (IBANs, dominios, teléfonos)
   ▼
[5. PERSISTIR] ─────────────> document_checks + invoice_fingerprint + structured_json
   │
   ▼
[6. AUTOMATIZACIÓN] ────────> reglas/webhooks (ya existente, se enriquece con checks)
```

### 3.1 Reglas de severidad

| Check (`check_type`) | Severidad | Condición |
| :--- | :--- | :--- |
| `math_discrepancy` | `OK` | Δ ≤ 0.02 € |
| `math_discrepancy` | `WARNING` | 0.02 < Δ ≤ 1.00 € |
| `math_discrepancy` | `CRITICAL` | Δ > 1.00 € |
| `bank_account_change` | `CRITICAL` | IBAN del documento no existe en el histórico del proveedor |
| `duplicate_invoice` | `CRITICAL` | Fingerprint igual a una huella persistida, o coincidencia difusa (±3 días, mismo proveedor/importe) |
| `threshold_avoidance` | `WARNING` | Serie de importes consecutivos justo bajo un umbral |
| `entity_resolution` | `INFO` | `AUTO_MERGE` / `FLAG_FOR_REVIEW` / `CREATE_NEW_ENTITY` (detalle en `detail_json`) |

### 3.2 Persistencia

Se persisten los checks **independientemente** del resultado. Si existe al menos un check `CRITICAL`, el documento se marca para revisión (el estado `Document.status` sigue `COMPLETED`; la revisión se gestiona con `documents.review_status`, ver §4).

---

## 4. Modelo de Datos (Migración Alembic)

### 4.1 Nueva tabla `document_checks`

| Columna | Tipo | Notas |
| :--- | :--- | :--- |
| `id` | UUID PK | |
| `organization_id` | UUID FK → `organizations.id` | Índice |
| `document_id` | UUID FK → `documents.id` | Índice |
| `check_type` | String | `math_discrepancy`, `bank_account_change`, `duplicate_invoice`, `threshold_avoidance`, `entity_resolution` |
| `severity` | String enum | `ok` / `warning` / `critical` / `info` |
| `status` | String enum | `open` / `acknowledged` |
| `title` | String | Descripción corta para UI |
| `detail_json` | JSON | Detalle estructurado (Δ, IBAN anterior/nuevo, fingerprint, etc.) |
| `created_at` | DateTime | |

### 4.2 Nueva tabla `entity_records`

| Columna | Tipo | Notas |
| :--- | :--- | :--- |
| `id` | UUID PK | |
| `organization_id` | UUID FK → `organizations.id` | Índice |
| `entity_id` | String | Identificador canónico asignado por `EntityResolutionEngine` |
| `name` | String | Razón social canónica |
| `tax_id` | String | NIF/CIF normalizado |
| `ibans_json` | JSON | Historial de IBANs validados (para `bank_account_change`) |
| `email_domain` | String | Dominio corporativo |
| `phone` | String | Teléfono normalizado E.164 |
| `created_at` / `updated_at` | DateTime | |

### 4.3 Nueva tabla `invoice_fingerprints`

| Columna | Tipo | Notas |
| :--- | :--- | :--- |
| `id` | UUID PK | |
| `organization_id` | UUID FK | Índice |
| `document_id` | UUID FK | |
| `fingerprint` | String | `SHA256(VendorTaxId‖CleanInvoiceNumber‖InvoiceDate‖TotalAmount)` |
| `vendor_tax_id` | String | |
| `invoice_number` | String | |
| `invoice_date` | Date | |
| `total_amount` | Float | |
| `created_at` | DateTime | |
| **Unique** | `(organization_id, fingerprint)` | Detección de duplicado exacto |

### 4.4 Cambios en tablas existentes

* `extraction_records` → nueva columna `structured_json` (JSON, nullable).
* `documents` → nuevas columnas `review_status` (String enum `unreviewed`/`reviewed`, default `unreviewed`), `reviewed_at` (DateTime, nullable), `reviewed_by` (UUID, nullable).

La migración se añade en `backend/alembic/versions/` con `python -m alembic revision --autogenerate -m "feat: invoice validation and review"`.

---

## 5. Contratos de API

### 5.1 `GET /api/v1/documents` (modificado)

Cada ítem de la lista se enriquece con el resumen de checks del documento:

```json
{
  "document_id": "8f8b8946-...",
  "organization_id": "default-org",
  "filename": "factura_suministros_2024.xlsx",
  "status": "completed",
  "review_status": "unreviewed",
  "check_summary": { "ok": 2, "warning": 1, "critical": 1, "info": 1 },
  "created_at": "2026-08-15T21:00:00.000000"
}
```

### 5.2 `GET /api/v1/documents/{document_id}` (modificado)

Añade `structured_invoice` (objeto `StructuredInvoice` o `null`) y `checks` (lista de `document_checks`):

```json
{
  "document_id": "8f8b8946-...",
  "status": "completed",
  "review_status": "unreviewed",
  "extraction": { "...": "..." },
  "structured_invoice": {
    "invoice_number": "F-2024-0982",
    "vendor_name": "Suministros Industriales S.L.",
    "vendor_tax_id": "B12345678",
    "issue_date": "2024-06-18",
    "currency": "EUR",
    "subtotal": 1250.50,
    "tax_total": 262.61,
    "total_amount": 1513.11,
    "items": [
      { "description": "Material oficina", "quantity": 10, "unit_price": 25.0, "tax_rate_pct": 21.0, "line_total": 250.0 }
    ],
    "tax_breakdown": [ { "tax_rate_pct": 21.0, "taxable_base": 1250.50, "tax_quota": 262.61 } ]
  },
  "checks": [
    {
      "id": "...",
      "check_type": "math_discrepancy",
      "severity": "critical",
      "status": "open",
      "title": "El total del documento difiere del recálculo en 12.30 €",
      "detail_json": { "delta": 12.30 },
      "created_at": "2026-08-18T..."
    }
  ]
}
```

### 5.3 `GET /api/v1/decision/checks` (NUEVO)

Lista hallazgos del tenant para la revisión visual. Query params: `document_id` (opcional), `severity` (`ok|warning|critical|info`), `status` (`open|acknowledged`), `limit` (1–500, default 100), `offset`.

```json
{ "items": [ { "...": "objeto document_check + filename del documento" } ], "total": 3 }
```

### 5.4 `POST /api/v1/documents/{document_id}/review` (NUEVO)

Marca un documento como revisado (acción del equipo financiero):

* **Payload:** `{ "note": "Revisado por contabilidad" }`
* **Efecto:** `documents.review_status = reviewed`, `reviewed_at = now`, `reviewed_by = usuario autenticado`. Checks asociados pasan a `status = acknowledged`.

### 5.5 `POST /api/v1/documents/upload` (sin cambios)

Multipart, `X-Organization-Id` + `Authorization: Bearer <jwt>` o `X-API-Key: fm_...`. El pipeline persistirá checks/structured_invoice automáticamente.

---

## 6. App de Escritorio PySide6 (Cliente del Backend)

### 6.1 Arquitectura

```
desktop/
├── main.py                        # Entry point (existente)
├── controllers/api_client.py      # EXTENDIDO: login, API key, org, documentos, checks, review
├── services/tray_agent.py         # EXTENDIDO: hot-folder → backend
├── models/table_model.py          # VirtualDataTableModel (existente)
└── ui/
    ├── main_window.py             # MODIFICADO: navegación QStackedWidget (Facturas / Detalle / Config)
    ├── login_dialog.py            # NUEVO: login JWT + modo API Key + selector de organización
    ├── documents_view.py          # NUEVO: lista de comprobantes con badges de severidad
    ├── invoice_review_view.py     # NUEVO: detalle de factura estructurada + hallazgos + revisar
    └── settings_view.py           # NUEVO: configuración hot-folder y API Key
```

### 6.2 Contrato del cliente API (`DesktopFlowMindClient`)

| Método | Endpoint backend | Autenticación |
| :--- | :--- | :--- |
| `login(email, password)` | `POST /api/v1/auth/login` | — |
| `me()` | `GET /api/v1/auth/me` | Bearer |
| `list_documents()` | `GET /api/v1/documents` | Bearer + `X-Organization-Id` |
| `get_document(id)` | `GET /api/v1/documents/{id}` | Bearer + `X-Organization-Id` |
| `list_checks(**filters)` | `GET /api/v1/decision/checks` | Bearer + `X-Organization-Id` |
| `review_document(id, note)` | `POST /api/v1/documents/{id}/review` | Bearer + `X-Organization-Id` |
| `upload_file(path)` | `POST /api/v1/documents/upload` (multipart) | API Key `X-API-Key` + `X-Organization-Id` |

### 6.3 Pantallas

* **LoginDialog:** email/contraseña → JWT; o API Key configurada; selector de organización (`me().organizations`).
* **DocumentsView:** tabla (QTableView + `VirtualDataTableModel`) con columnas: proveedor, nº factura, fecha, total, estado, y **badge de severidad** (verde/ámbar/rojo según `check_summary.critical/warning`). Doble clic → detalle.
* **InvoiceReviewView:** cabecera (proveedor, NIF, nº factura, fechas, divisa), tabla de ítems (QTableView), resumen de impuestos y totales (recalculados vs impresos), **panel de hallazgos** (`document_checks`) con colores por severidad, y botón **"Marcar como revisada"** (→ `review_document`).
* **SettingsView:** carpetas de entrada/salida del hot-folder, API Key (pegada desde `/settings` del backend), botones iniciar/parar el agente y log de actividad.

---

## 7. Automatización: Hot-Folder → Backend

### 7.1 Flujo

```text
[Carpeta monitorizada] ──> HotFolderWatcher.on_created
   │
   ▼
[DesktopFlowMindClient.upload_file(path)]
   │  POST /api/v1/documents/upload
   │  Headers: X-API-Key: fm_...  ·  X-Organization-Id: ...
   ▼
[Backend: persistir → pipeline → validar → reglas/webhooks]
   │
   ▼
[Notificación QSystemTrayIcon con document_id/estado]
```

### 7.2 Cambios en `services/tray_agent.py`

* `HotFolderHandler._process_file` pasa de `process_file_locally` (local, se conserva como modo offline opcional) a **`send_to_backend`** cuando hay API Key configurada.
* `api_client.send_to_backend` se actualiza para usar API Key (`X-API-Key`) en lugar de solo Bearer, y a `POST /api/v1/documents/upload`.
* Log persistido en la BD del backend (el propio `Document`); el agente muestra el estado final consultando `GET /documents/{id}`.

---

## 8. Tests

| Área | Archivo de test | Casos |
| :--- | :--- | :--- |
| Structurizer | `tests/test_invoice_structurizer.py` | Cabecera desde campos canónicos; ítems con fuzzy match de columnas; desglose IVA por tramo; totales; sin líneas. |
| Pipeline validado | `tests/test_invoice_pipeline.py` | Subida de factura → `structured_invoice` persistido; checks creados con severidad correcta; duplicado exacto detectado en 2ª carga; documento con revisión. |
| API de revisión | `tests/test_invoice_review_api.py` | `GET /documents` con `check_summary`; `GET /decision/checks` filtrado por severidad/estado; `POST /documents/{id}/review` (aislamiento multi-tenant). |
| Desktop | `tests/test_desktop_invoice_review.py` | `DesktopFlowMindClient` contra backend real (httpx + AsyncClient); tray_agent envía a `/upload` con API key. |

## 9. Definition of Done

- [ ] `StructuredInvoice` tipado y `InvoiceStructurizer` con casos borde.
- [ ] Pipeline ejecuta validadores para `invoice` y persiste `document_checks`, `entity_records` e `invoice_fingerprints`.
- [ ] Endpoints de revisión implementados y con tests de aislamiento multi-tenant.
- [ ] App PySide6 navegable: lista con badges, detalle con hallazgos y revisión.
- [ ] Hot-folder → backend funcional con API Key y notificaciones.
- [ ] Migración Alembic aplicable desde cero (`upgrade head`).
- [ ] Documentación actualizada (API reference, arquitectura, roadmap) y entradas en `CHANGELOG.md`.
- [ ] Sin llamadas a LLMs externos; sin secretos en el repositorio.