# División de Trabajo en 4 Personas — Proyecto 4 (Extractor, Validador y Reconciliador de Facturas)

Este documento define **cómo se reparte la implementación del Proyecto 4 entre 4 personas**, qué módulos, archivos y tests son propiedad de cada una, **la tarea exacta de cada una** y **los pasos a seguir** para completarla.

---

## 1. Reglas generales del equipo

1. **No colisión de archivos:** en cada tarea, ningún archivo se modifica por más de una persona. Si se necesita tocar un archivo ajeno, se coordina antes.
2. **Conventional Commits** (ver `AGENTS.md` §15): `feat:`, `fix:`, `test:`, `refactor:`, `docs:`.
3. **Commits pequeños y descriptivos**, nunca genéricos.
4. **Definition of Done por módulo** (ver `docs/04-engineering/04-invoice-validation-review.md` §9).
5. Cada persona documenta su módulo (docs técnicas + entrada en `CHANGELOG.md`) al terminar.
6. **Ningún push directo a `main` sin integración y suite de tests en verde** (aplica también si se usan worktrees, ver `scripts/agent-orchestration.md`).
7. **El contrato JSON del TDD §5 es la fuente de verdad** entre las personas que consumen la API: si un shape cambia, se actualiza primero el TDD y luego se coordina.

---

## 2. Mapa de personas

| | **P1 — Backend Core** | **P2 — Backend API de Revisión** | **P3 — App de Escritorio (UI Financiera)** | **P4 — Automatización Hot-Folder + Integración** |
| :--- | :--- | :--- | :--- | :--- |
| **Tarea** | Dominio de factura estructurada + conectar validadores al pipeline | Endpoints de revisión visual | Interfaz de gestión financiera en PySide6 | Hot-folder → backend + integración final |
| **Fase (TDD)** | Fase 1 | Fase 2 | Fase 3 (UI) | Fase 4 + integración |
| **Área** | `backend/app/domain/`, `backend/app/services/invoice/`, `pipeline.py`, `infrastructure/models.py`, migración Alembic | `backend/app/api/routers/` (documents, decision), DTOs de respuesta | `desktop/controllers/api_client.py`, `desktop/ui/` (login, documents, invoice_review, main_window) | `desktop/services/tray_agent.py`, `desktop/ui/settings_view.py`, integración y docs finales |

---

## 3. Persona 1 — Backend Core (dominio + pipeline)

### Tarea
Crear el **modelo de factura estructurada** (`StructuredInvoice`) y **conectar los validadores deterministas al pipeline** de procesamiento, persistiendo hallazgos (`document_checks`), entidades canónicas (`entity_records`) y huellas de facturas (`invoice_fingerprints`).

### Archivos propios
- `backend/app/domain/invoice_models.py` (NUEVO): `InvoiceLineItem`, `TaxBreakdownItem`, `StructuredInvoice`.
- `backend/app/services/invoice/__init__.py` + `backend/app/services/invoice/structurizer.py` (NUEVO).
- `backend/app/services/pipeline.py` (MODIFICAR).
- `backend/app/services/decision/` (`mathematical_validator.py`, `sentinel.py`, `entity_resolution.py`) — solo lo necesario para recibir histórico real desde BD.
- `backend/app/infrastructure/models.py` (MODIFICAR): `DocumentCheck`, `EntityRecord`, `InvoiceFingerprint`; columnas `ExtractionRecord.structured_json`, `Document.review_status/reviewed_at/reviewed_by`.
- `backend/alembic/versions/xxx_invoice_validation_review.py` (NUEVO): migración.

### Pasos a seguir
1. Leer `docs/04-engineering/04-invoice-validation-review.md` §2 y §4.
2. Crear `invoice_models.py` con los modelos Pydantic v2 tipados (TDD §2.1).
3. Implementar `InvoiceStructurizer` (TDD §2.2): cabecera desde keys canónicas → ítems con fuzzy match (`rapidfuzz`) → desglose IVA → totales. Reutilizar `SchemaNormalizer.normalize_value`.
4. Revisar firmas de `MathematicalDocumentValidator.validate_invoice`, `FlowMindSentinel.audit_document` y `EntityResolutionEngine.resolve`; adaptar para recibir el histórico real desde BD (IBANs y fingerprints). **No tocar los routers** (es de P2).
5. Añadir tablas y columnas a `models.py` (TDD §4).
6. Generar y aplicar la migración: `cd backend && python -m alembic revision --autogenerate -m "feat: invoice validation and review" && python -m alembic upgrade head`. Verificar con `python -m alembic current`.
7. Modificar `process_document_pipeline`: si `document_type == invoice`, ejecutar structurizer → validación matemática → Sentinel → resolución de entidades → persistir checks/huellas/entidades/`structured_json` (TDD §3).
8. Escribir tests `tests/test_invoice_structurizer.py` y `tests/test_invoice_pipeline.py` (casos borde: sin líneas, IVA por tramos, duplicado en 2ª carga).
9. Correr la suite: `python -m pytest tests/`.
10. Documentar: actualizar `docs/04-engineering/02-database.md` (nuevas tablas) y añadir entrada al `CHANGELOG.md`.

### Entrega clave a P2
Modelos finales (`StructuredInvoice`, `DocumentCheck`) y pipeline funcional con persistencia.

### Criterio de finalización
Migración aplicable desde cero (`upgrade head`), pipeline persiste checks/entidades/huellas, tests en verde.

---

## 4. Persona 2 — Backend API de Revisión

### Tarea
Exponer los **endpoints de revisión visual** que consume la app de escritorio: listas enriquecidas, hallazgos filtrables y acción de marcar un documento como revisado.

### Archivos propios
- `backend/app/api/routers/documents.py` (MODIFICAR): enriquecer `GET /documents` y `GET /documents/{id}`.
- `backend/app/api/routers/decision.py` (MODIFICAR): eliminar mocks; añadir `GET /decision/checks`.
- `backend/app/api/routers/review.py` (NUEVO, opcional) o endpoint `POST /documents/{id}/review` en `documents.py`.
- `backend/app/domain/` DTOs de respuesta de revisión (reutilizando `invoice_models.py` de P1).

### Pasos a seguir
1. Leer `docs/04-engineering/04-invoice-validation-review.md` §5.
2. Enriquecer `GET /api/v1/documents` con `check_summary` y `review_status` (TDD §5.1).
3. Enriquecer `GET /api/v1/documents/{id}` con `structured_invoice` y `checks` (TDD §5.2).
4. Crear `GET /api/v1/decision/checks` con filtros `document_id`, `severity`, `status`, `limit`, `offset` (TDD §5.3).
5. Crear `POST /api/v1/documents/{id}/review` → `review_status=reviewed`, `reviewed_at`, `reviewed_by`, checks a `acknowledged` (TDD §5.4).
6. **Eliminar los datos mock** del router `decision.py` (entidades/histórico hardcodeados) y conectar con la persistencia real de P1.
7. Verificar **aislamiento multi-tenant** en cada endpoint: todas las consultas filtran por `organization_id` (ver `AGENTS.md` §12).
8. Escribir `tests/test_invoice_review_api.py` (incluye aislamiento entre organizaciones).
9. Correr la suite: `python -m pytest tests/`.
10. Documentar: actualizar `docs/04-engineering/01-api-reference.md` y añadir entrada al `CHANGELOG.md`.

### Entrega clave a P3
Contrato JSON final de los endpoints (debe coincidir con TDD §5).

### Criterio de finalización
Endpoints responden según TDD §5, sin mocks en routers, tests de API con aislamiento en verde.

---

## 5. Persona 3 — App de Escritorio (UI Financiera)

### Tarea
Construir la **interfaz de gestión financiera en PySide6**: login, lista de comprobantes con badges de anomalía, detalle de factura estructurada con hallazgos y acción de revisión.

### Archivos propios
- `desktop/controllers/api_client.py` (MODIFICAR): `login`, `me`, `list_documents`, `get_document`, `list_checks`, `review_document`, `upload_file`.
- `desktop/ui/login_dialog.py` (NUEVO).
- `desktop/ui/main_window.py` (MODIFICAR): navegación `QStackedWidget`.
- `desktop/ui/documents_view.py` (NUEVO).
- `desktop/ui/invoice_review_view.py` (NUEVO).
- `desktop/models/table_model.py` (REUTILIZAR `VirtualDataTableModel`).

### Pasos a seguir
1. Leer `docs/04-engineering/04-invoice-validation-review.md` §6 (contrato `api_client` y pantallas).
2. Implementar en `api_client.py` los métodos del contrato (TDD §6.2) usando `httpx`. Mientras P2 no esté listo, validar contra **mocks que respeten los shapes del TDD §5**.
3. Crear `login_dialog.py`: login JWT (email/contraseña), modo API Key, selector de organización desde `me().organizations`.
4. Modificar `main_window.py`: `QStackedWidget` con navegación (Facturas / Detalle / Configuración). La entrada "Configuración" carga `SettingsView` **de forma perezosa** (import dentro de función + `try/except`), porque `settings_view.py` lo crea P4.
5. Crear `documents_view.py`: `QTableView` con `VirtualDataTableModel` — columnas proveedor, nº factura, fecha, total, estado — y **badge de severidad** según `check_summary.critical/warning`. Doble clic → detalle.
6. Crear `invoice_review_view.py`: cabecera (proveedor, NIF, nº, fechas, divisa), tabla de ítems, resumen de impuestos y totales (recalculados vs impresos), **panel de hallazgos** (`document_checks`) coloreado por severidad y botón **"Marcar como revisada"** → `review_document`.
7. Escribir `tests/test_desktop_invoice_review.py`: `DesktopFlowMindClient` contra backend real (AsyncClient + fixtures de `conftest.py`).
8. Correr la suite: `python -m pytest tests/`.
9. Documentar: actualizar `docs/03-architecture/03-desktop-pyside6.md` (arquitectura real de pantallas) y añadir entrada al `CHANGELOG.md`.

### Entregable a P4
`api_client.upload_file` implementado y la navegación de `main_window` preparada para integrar `SettingsView`.

### Criterio de finalización
App navegable end-to-end contra backend: lista con badges, detalle con hallazgos y revisión funcional.

---

## 6. Persona 4 — Automatización Hot-Folder → Backend + Integración

### Tarea
Integrar el **agente de bandeja (hot-folder) con el backend** para que, al depositar un archivo, se persista en la BD, se valide y se disparen reglas/webhooks. Coordinar la **integración final** del vertical.

### Archivos propios
- `desktop/services/tray_agent.py` (MODIFICAR): `HotFolderHandler` y `HotFolderWatcher`.
- `desktop/ui/settings_view.py` (NUEVO): interfaz de configuración del agente.
- (Solo lectura) `desktop/controllers/api_client.py` (de P3): usar `upload_file` y `list_documents`.

### Pasos a seguir
1. Leer `docs/04-engineering/04-invoice-validation-review.md` §7 y el estado real de `desktop/services/tray_agent.py` y `desktop/controllers/api_client.py` (el método `send_to_backend` existe pero no se usa).
2. Coordinar con P3 la interfaz de `SettingsView` (QWidget con señales/atributos: carpetas in/out, API key, iniciar/parar, log).
3. Crear `settings_view.py`: campos de carpetas de entrada/salida, campo de API Key (`fm_...`), selector de organización, botones iniciar/parar el agente y `QPlainTextEdit` de log.
4. En `tray_agent.py`: `_process_file` → si hay API Key configurada, enviar con `upload_file` (multipart + `X-API-Key` + `X-Organization-Id`); conservar el modo local como opción offline.
5. Añadir notificaciones `QSystemTrayIcon.showMessage()` (éxito/alerta) y, opcionalmente, polling de `GET /documents/{id}` para el estado final.
6. Escribir `tests/test_desktop_automation.py`: depositar un archivo → `upload_file` recibe el documento persistido en el backend.
7. Correr la suite completa: `python -m pytest tests/`.
8. **Integración final (orquestador/P4):** fusionar las partes, verificar que la UI de P3 contra los endpoints reales de P2 funciona, resolver conflictos de contrato, sincronizar documentación final y consolidar `CHANGELOG.md`.
9. Actualizar el roadmap: `docs/01-product/03-roadmap.md` (marcar items completados de la Fase 10) y `docs/01-product/04-proyecto4-alineacion-tarea.md` (estado de brechas).

### Criterio de finalización
Archivo depositado en la carpeta → documento persistido en BD con checks + notificación mostrada. Suite completa en verde.

---

## 7. Contratos de interfaz entre personas

| Interfaz | Definido en | Responsable | Consumidor |
| :--- | :--- | :--- | :--- |
| `StructuredInvoice`, `DocumentCheck`, `EntityRecord`, `InvoiceFingerprint` | TDD §2 y §4 | P1 | P2 |
| `GET /api/v1/documents` (+ `check_summary`/`review_status`) | TDD §5.1 | P2 | P3 |
| `GET /api/v1/documents/{id}` (+ `structured_invoice`/`checks`) | TDD §5.2 | P2 | P3 |
| `GET /api/v1/decision/checks` | TDD §5.3 | P2 | P3 |
| `POST /api/v1/documents/{id}/review` | TDD §5.4 | P2 | P3 |
| `POST /api/v1/documents/upload` (multipart + API Key) | TDD §5.5 (sin cambios) | Backend (sin dueño nuevo) | P3/P4 |
| `api_client.upload_file` | TDD §6.2 | P3 | P4 |
| `SettingsView` (interfaz QWidget) | TDD §6.3 + §6 de este doc | P4 | P3 (main_window carga perezosa) |

> Regla de oro: **el contrato JSON del TDD §5 es la fuente de verdad entre P2 y P3.** P3 no espera a P2 para construir la UI; usa mocks que respeten esos shapes.

---

## 8. Secuencia y dependencias

```text
P1 (dominio + pipeline + migración)   ← arranca primero
   │  entrega modelos/contract
   ▼
P2 (endpoints de revisión)            ← puede arrancar al validarse la migración
   │  entrega contrato JSON final
   ▼
P3 (UI PySide6)                       ← arranca en paralelo contra mocks del TDD
   │  entrega api_client.upload_file + main_window preparado
   ▼
P4 (hot-folder → backend)             ← arranca tras P3 (o en paralelo con TDD §7)
   │
   ▼
Integración final + suite completa + docs finales + CHANGELOG global (P4 / orquestador)
```

**Solapamiento recomendado:**
- P1 y P3 empiezan el día 1 (P3 con mocks).
- P2 arranca al validarse la migración de P1.
- P4 arranca cuando `api_client.upload_file` de P3 esté listo (o en paralelo diseñando `SettingsView`).

---

## 9. Criterios de finalización por persona

| Persona | ¿Cuándo termina? |
| :--- | :--- |
| **P1** | Migración aplicable `upgrade head`; pipeline de factura persiste checks/entidades/huellas; tests de structurizer y pipeline en verde. |
| **P2** | Endpoints enriquecidos y de revisión responden según TDD §5; tests de API en verde; sin mocks en routers. |
| **P3** | App navegable (lista con badges, detalle con hallazgos, revisión funcional); `api_client.upload_file` entregado; tests de escritorio en verde. |
| **P4** | Hot-folder envía a `/upload` con API Key y notifica; suite completa en verde; documentación sincronizada y CHANGELOG consolidado. |