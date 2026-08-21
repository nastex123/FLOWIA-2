# Registro de Cambios e Implementación de Backend — Luis (P1 + P2)

**Proyecto:** FlowMind AI — Extractor, Validador y Reconciliador de Facturas y Comprobantes  
**Responsable:** Luis (Persona 1: Backend Core + Persona 2: Backend API de Revisión)  
**Referencias:** 
- Plan de Trabajo del Equipo: [02-trabajo-equipo-proyecto4.md](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/docs/08-operations/02-trabajo-equipo-proyecto4.md)
- Diseño Técnico TDD: [04-invoice-validation-review.md](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/docs/04-engineering/04-invoice-validation-review.md)

---

## 1. Matriz de Cumplimiento de Requerimientos

### Persona 1 — Backend Core (Dominio, Structurizer, Persistencia y Pipeline)

| Requerimiento TDD / Operaciones | Archivo / Componente | Estado | Detalle de Implementación |
| :--- | :--- | :---: | :--- |
| **Modelos Pydantic v2 de Factura** | [`backend/app/domain/invoice_models.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/app/domain/invoice_models.py) | **COMPLETADO** | Creados `InvoiceLineItem`, `TaxBreakdownItem`, `StructuredInvoice` y `DocumentCheckDTO`. |
| **Motor Structurizer Determinista** | [`backend/app/services/invoice/structurizer.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/app/services/invoice/structurizer.py) | **COMPLETADO** | Creado `InvoiceStructurizer`: mapeo difuso de columnas con `rapidfuzz` ($\ge 0.70$), normalización Unicode sin tildes, extracción de ítems y cálculo de desglose de IVA por tramos. |
| **Extensión de Modelos ORM** | [`backend/app/infrastructure/models.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/app/infrastructure/models.py) | **COMPLETADO** | Creadas entidades `DocumentCheck`, `EntityRecord`, `InvoiceFingerprint`. Añadidas columnas `review_status`, `reviewed_at`, `reviewed_by` a `Document` y `structured_json` a `ExtractionRecord`. |
| **Migración Alembic** | [`backend/alembic/versions/2fa027476344_feat_invoice_validation_and_review.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/alembic/versions/2fa027476344_feat_invoice_validation_and_review.py) | **COMPLETADO** | Generada y aplicada con `op.batch_alter_table` para soporte cruzado SQLite/PostgreSQL. Estado verificado en `head`. |
| **Integración en Pipeline** | [`backend/app/services/pipeline.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/app/services/pipeline.py) | **COMPLETADO** | Ejecución secuencial cuando `document_type == "invoice"`: estructurador $\rightarrow$ validación matemática $\rightarrow$ Sentinel $\rightarrow$ resolución de entidades $\rightarrow$ persistencia de checks y huellas. |
| **Tests Unitarios e Integración P1** | [`tests/test_invoice_structurizer.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/tests/test_invoice_structurizer.py), [`tests/test_invoice_pipeline.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/tests/test_invoice_pipeline.py) | **COMPLETADO** | 5 tests automatizados cubriendo casos borde (sin líneas, múltiples tramos de IVA, detección de duplicados en 2ª carga). |

---

### Persona 2 — Backend API de Revisión (Endpoints REST y Auditoría)

| Requerimiento TDD / Operaciones | Archivo / Componente | Estado | Detalle de Implementación |
| :--- | :--- | :---: | :--- |
| **Lista Enriquecida `GET /documents`** | [`backend/app/api/routers/documents.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/app/api/routers/documents.py) | **COMPLETADO** | Devuelve `review_status` y agregación `check_summary` (`ok`, `warning`, `critical`, `info`). |
| **Detalle de Factura `GET /documents/{id}`** | [`backend/app/api/routers/documents.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/app/api/routers/documents.py) | **COMPLETADO** | Devuelve `structured_invoice` y lista detallada de `checks` asociados al documento. |
| **Acción de Revisión `POST /documents/{id}/review`** | [`backend/app/api/routers/documents.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/app/api/routers/documents.py) | **COMPLETADO** | Actualiza `review_status = "reviewed"`, `reviewed_at`, `reviewed_by` y pasa los checks asociados a `acknowledged`. |
| **Listado de Hallazgos `GET /decision/checks`** | [`backend/app/api/routers/decision.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/app/api/routers/decision.py) | **COMPLETADO** | Nuevo endpoint con filtros por `document_id`, `severity`, `status`, paginación (`limit`, `offset`) y nombre de archivo adjunto. |
| **Eliminación de Mocks en Decision API** | [`backend/app/api/routers/decision.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/app/api/routers/decision.py) | **COMPLETADO** | Eliminados datos hardcodeados en `/entities/resolve` y `/sentinel-audit`; conectados a `EntityRecord` e `InvoiceFingerprint` de la base de datos real. |
| **Aislamiento Multi-Tenant Estricto** | Todo el router de API | **COMPLETADO** | Cada endpoint filtra obligatoriamente por `organization_id == auth.org_id`. |
| **Tests de API y Aislamiento P2** | [`tests/test_invoice_review_api.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/tests/test_invoice_review_api.py), [`tests/test_decision_api.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/tests/test_decision_api.py) | **COMPLETADO** | 8 tests verificando contratos JSON, acción de revisión, filtrado de checks e inaccesibilidad entre organizaciones (404 estricto). |

---

## 2. Detalle de Archivos Creados y Modificados

### 2.1 Archivos Creados

1. [`backend/app/domain/invoice_models.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/app/domain/invoice_models.py)
   - Define el esquema tipado de la factura:
     - `InvoiceLineItem`: Líneas individuales con descripción, cantidad, precio, descuento, tipo de IVA y total de línea.
     - `TaxBreakdownItem`: Desglose impositivo agrupado por tipo impositivo (`tax_rate_pct`, `taxable_base`, `tax_quota`).
     - `StructuredInvoice`: Entidad canónica completa con metadatos de cabecera, desglose impositivo y totales calculados.
     - `DocumentCheckDTO`: Esquema de transferencia para hallazgos visuales.

2. [`backend/app/services/invoice/__init__.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/app/services/invoice/__init__.py)
   - Exporta `InvoiceStructurizer`.

3. [`backend/app/services/invoice/structurizer.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/app/services/invoice/structurizer.py)
   - Contiene la lógica de transformación de `ExtractionResult` a `StructuredInvoice`.
   - Incorpora `_normalize_text` (remoción de acentos con `unicodedata` y caracteres de puntuación).
   - Realiza mapeo difuso de encabezados (`HEADER_FIELD_MAPPINGS`) y columnas tabulares (`LINE_ITEM_COLUMN_CANDIDATES`).
   - Implementa `_clean_number` para sanear importes con símbolos (`€`, `$`, `%`).
   - Agrupa líneas por tipo impositivo para construir el `tax_breakdown`.

4. [`backend/alembic/versions/2fa027476344_feat_invoice_validation_and_review.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/alembic/versions/2fa027476344_feat_invoice_validation_and_review.py)
   - Migración de base de datos que crea las tablas `entity_records`, `document_checks`, `invoice_fingerprints` y modifica `documents` y `extraction_records` usando `op.batch_alter_table`.

5. [`tests/test_invoice_structurizer.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/tests/test_invoice_structurizer.py)
   - Pruebas unitarias para extracción completa con tabla, facturas sólo con cabecera y desglose multidivisa/multitasa.

6. [`tests/test_invoice_pipeline.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/tests/test_invoice_pipeline.py)
   - Pruebas integradas del pipeline persistiendo checks, huellas y detección de duplicados en segunda carga.

7. [`tests/test_invoice_review_api.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/tests/test_invoice_review_api.py)
   - Pruebas de integración de la API REST para los endpoints de documentos, checks, acción de revisión y aislamiento estricto entre tenants.

---

### 2.2 Archivos Modificados

1. [`backend/app/infrastructure/models.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/app/infrastructure/models.py)
   - Añadidas clases ORM: `DocumentCheck`, `EntityRecord`, `InvoiceFingerprint`.
   - Modificado `Document`: añadidas columnas `review_status` (default `"unreviewed"`), `reviewed_at`, `reviewed_by` y relaciones `checks` y `fingerprints`.
   - Modificado `ExtractionRecord`: añadida columna `structured_json` (JSON nullable).

2. [`backend/app/services/pipeline.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/app/services/pipeline.py)
   - Añadida sección específica tras la clasificación cuando `document_type == "invoice"`:
     1. Invocación de `InvoiceStructurizer`.
     2. Validación matemática con `MathematicalDocumentValidator` generando checks de tipo `math_discrepancy`.
     3. Búsqueda y generación de huella `InvoiceFingerprint` con `FlowMindSentinel` generando check `duplicate_invoice` ante colisión.
     4. Detección de IBAN y comprobación de cambio no verificado generando check `bank_account_change`.
     5. Resolución de entidad con `EntityResolutionEngine` persistiendo o actualizando `EntityRecord` y generando check `entity_resolution`.
     6. Persistencia de `structured_json` en `ExtractionRecord` y almacenamiento en base de datos.

3. [`backend/app/api/routers/documents.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/app/api/routers/documents.py)
   - `GET /api/v1/documents`: Enriquecido para agregar `review_status` y `check_summary`.
   - `GET /api/v1/documents/{document_id}`: Enriquecido para incluir `structured_invoice` y lista de `checks`.
   - `POST /api/v1/documents/{document_id}/review`: Implementado para actualizar estado y cambiar checks a `acknowledged`.

4. [`backend/app/api/routers/decision.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/backend/app/api/routers/decision.py)
   - Conectados los endpoints `/entities/resolve` y `/sentinel-audit` a consultas reales de SQLAlchemy sobre `EntityRecord` e `InvoiceFingerprint`.
   - Añadido endpoint `GET /api/v1/decision/checks` con filtros de severidad, estado y documento.

5. [`tests/conftest.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/tests/conftest.py)
   - Actualizado el fixture `clean_db` a `@pytest_asyncio.fixture(autouse=True)` asíncrono para prevenir bloqueos de conexiones en SQLite.

6. [`tests/test_decision_api.py`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/tests/test_decision_api.py)
   - Adaptadas las pruebas para sembrar entidades y huellas reales en base de datos antes de verificar los endpoints de decisión.

7. [`docs/04-engineering/01-api-reference.md`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/docs/04-engineering/01-api-reference.md)
   - Documentados los contratos exactos de respuesta de `GET /documents`, `GET /documents/{id}`, `POST /documents/{id}/review` y `GET /decision/checks`.

8. [`docs/04-engineering/02-database.md`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/docs/04-engineering/02-database.md)
   - Documentadas las nuevas tablas, relaciones, campos de auditoría y la nueva revisión de migración Alembic.

9. [`CHANGELOG.md`](file:///C:/Users/marsh/OneDrive/Documents/Visual_Studio_Workshps/FLOWIA-2/FLOWIA-2/CHANGELOG.md)
   - Registrada la entrada oficial correspondiente a la implementación de Backend del Proyecto 4.

---

## 3. Contratos de API Entregados a Frontend (Brandon / P3)

Los siguientes contratos corresponden a la especificación acordada en el TDD §5 y se encuentran 100% operativos:

### 3.1 `GET /api/v1/documents`
```json
[
  {
    "document_id": "8f8b8946-b6b8-4775-9b2f-981881775791",
    "organization_id": "default-org",
    "filename": "factura_suministros_2024.xlsx",
    "file_size_bytes": 6230,
    "status": "completed",
    "review_status": "unreviewed",
    "check_summary": {
      "ok": 2,
      "warning": 1,
      "critical": 1,
      "info": 1
    },
    "created_at": "2026-08-20T07:45:00.000000"
  }
]
```

### 3.2 `GET /api/v1/documents/{document_id}`
```json
{
  "document_id": "8f8b8946-b6b8-4775-9b2f-981881775791",
  "organization_id": "default-org",
  "filename": "factura_suministros_2024.xlsx",
  "file_size_bytes": 6230,
  "status": "completed",
  "review_status": "unreviewed",
  "reviewed_at": null,
  "reviewed_by": null,
  "created_at": "2026-08-20T07:45:00.000000",
  "error_message": null,
  "extraction": {
    "document_type": "invoice",
    "confidence": 0.95,
    "fields": { "...": "..." },
    "tables": [],
    "processing_time_ms": 42.5
  },
  "structured_invoice": {
    "document_id": "8f8b8946-b6b8-4775-9b2f-981881775791",
    "invoice_number": "F-2024-0982",
    "vendor_name": "Suministros Industriales S.L.",
    "vendor_tax_id": "B12345678",
    "customer_name": "Acme Corp SA",
    "customer_tax_id": "A87654321",
    "issue_date": "2024-06-18",
    "due_date": "2024-07-18",
    "currency": "EUR",
    "subtotal": 1250.50,
    "tax_total": 262.61,
    "total_amount": 1513.11,
    "items": [
      {
        "description": "Material de oficina",
        "quantity": 10.0,
        "unit_price": 25.0,
        "discount_pct": 0.0,
        "tax_rate_pct": 21.0,
        "line_total": 250.0
      }
    ],
    "tax_breakdown": [
      {
        "tax_rate_pct": 21.0,
        "taxable_base": 1250.50,
        "tax_quota": 262.61
      }
    ]
  },
  "checks": [
    {
      "id": "chk-001",
      "document_id": "8f8b8946-b6b8-4775-9b2f-981881775791",
      "check_type": "math_discrepancy",
      "severity": "critical",
      "status": "open",
      "title": "El total del documento difiere del recálculo en 12.30 €",
      "detail_json": { "deviation": 12.30 },
      "created_at": "2026-08-20T07:45:01.000000"
    }
  ]
}
```

### 3.3 `POST /api/v1/documents/{document_id}/review`
```json
{
  "status": "reviewed",
  "document_id": "8f8b8946-b6b8-4775-9b2f-981881775791",
  "reviewed_at": "2026-08-20T08:00:00.000000",
  "reviewed_by": "user-uuid-1234",
  "acknowledged_checks_count": 3,
  "note": "Revisado por contabilidad"
}
```

### 3.4 `GET /api/v1/decision/checks`
```json
{
  "items": [
    {
      "id": "chk-001",
      "document_id": "8f8b8946-b6b8-4775-9b2f-981881775791",
      "filename": "factura_suministros_2024.xlsx",
      "check_type": "duplicate_invoice",
      "severity": "critical",
      "status": "open",
      "title": "Factura duplicada detectada: coincide con documento doc-prev-01...",
      "detail_json": { "duplicate_document_id": "doc-prev-01" },
      "created_at": "2026-08-20T07:45:01.000000"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

---

## 4. Estado de la Suite de Pruebas

Ejecución de la suite completa de pruebas del repositorio:

```text
======================== 98 passed in 93.42s ========================
```

Todos los módulos existentes y nuevos (autenticación, extracción tabular, visión, pipeline local, pipeline de facturas, structurizer, review API, decision API, fact graph, OMR, SII, Verifactu) superaron las pruebas unitarias y de integración satisfactoriamente.
