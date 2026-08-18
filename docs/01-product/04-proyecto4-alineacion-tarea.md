# Alineación de la Tarea Asignada con FlowMind AI — Extractor, Validador y Reconciliador de Facturas y Comprobantes

Este documento especifica **en qué se asemeja la tarea asignada (Proyecto 4) con el proyecto FlowMind AI**, qué capacidades ya cubren cada requisito, qué brechas existen y qué se propone construir en esta iteración.

---

## 1. La Tarea Asignada (Proyecto 4)

### Proyecto 4: Extractor, Validador y Reconciliador de Facturas y Comprobantes

* **El Problema:** El departamento financiero procesa facturas en formato PDF o imágenes con diseños totalmente heterogéneos, requiriendo captura manual propensa a errores humanos.
* **La App:** Una interfaz de gestión financiera donde el equipo revisa documentos subidos, visualiza los campos extraídos estructurados (proveedor, ítems, impuestos, totales) y detecta anomalías o discrepancias de forma visual.
* **La Automatización:** Un observador de directorios (folder watcher) o conector de correo que detecta la llegada de nuevos comprobantes adjuntos, extrae la información clave, valida las reglas de negocio y alimenta automáticamente una base de datos o sistema contable.

---

## 2. Mapeo Requisito-Tarea ↔ Capacidad FlowMind AI ↔ Brecha ↔ Solución

| Pilar de la tarea | Requisito | Capacidad existente en FlowMind AI | Brecha | Solución propuesta en esta iteración |
| :--- | :--- | :--- | :--- | :--- |
| **Problema** | Procesar facturas PDF / imágenes con diseños heterogéneos | Motores de extracción local: `PDFExtractor` (PyMuPDF + pdfplumber, con fallback OCR), `VisionExtractor` (OCR, QR/1D, dewarping), `TabularExtractor` (pandas/openpyxl), `RuleExtractor` (regex), `MLClassifier` / `RuleClassifier`. Pipeline `upload → extract → classify → persist`. | Las facturas se extraen como campos genéricos (`fields_json`) y tablas crudas, **sin un modelo de dominio de factura estructurado** (proveedor, ítems, impuestos, totales). | Crear dominio `StructuredInvoice` y servicio `InvoiceStructurizer` que adapte la extracción a una factura tipada (P1). |
| **La App** | Revisión de documentos, campos estructurados (proveedor, ítems, impuestos, totales) y detección visual de anomalías | Backend expone endpoints de decisión/negocio (validate-math, sentinel-audit, three-way-match). El frontend web Next.js existe como andamiaje pero **no compila** (falta `frontend/src/lib/`). | No hay una interfaz de gestión financiera funcional ni visualización de anomalías. Los validadores (matemático, Sentinel) **no están conectados al pipeline** y usan datos mock. | **Migrar el cliente a la app de escritorio PySide6** (ver ADR-003): pantallas de revisión de facturas con badges de severidad y panel de hallazgos. Conectar validadores al pipeline y persistir hallazgos (`document_checks`). Endpoints de revisión (P2). UI de escritorio (P3). |
| **La Automatización** | Folder watcher / correo que detecta comprobantes, extrae, valida reglas y alimenta BD automáticamente | `HotFolderWatcher` (desktop, con `watchdog`) detecta archivos, pero **procesa 100% local** escribiendo JSON en una carpeta; no alimenta la BD del backend. Reglas de automatización + webhooks ya se disparan en el pipeline. | El hot-folder no usa el pipeline persistente del backend (no persiste, no valida, no dispara reglas/webhooks). No hay conector IMAP. | **Hot-folder → backend**: el agente envía cada archivo a `POST /api/v1/documents/upload` con API Key (`fm_...`), el backend persiste, valida y dispara reglas/webhooks. (P3). Conector IMAP queda como propuesta futura (Fase 12 del roadmap). |

---

## 3. Análisis de Brechas & Estado de Ejecución

Estado real verificado en el código del repositorio:

| Capacidad | Estado | Responsable | Detalle |
| :--- | :---: | :--- | :--- |
| Motores de extracción (tabular, PDF, visión/OCR, reglas) | ✅ Implementado | Core | `PDFExtractor`, `VisionExtractor`, `TabularExtractor` |
| Pipeline end-to-end con persistencia SQLite/Postgres | ✅ Implementado | Core | Asíncrono, multi-tenant y seguro |
| Clasificación híbrida (reglas + ML clásico) | ✅ Implementado | Core | `scikit-learn` TF-IDF + heurísticas |
| Reglas de negocio + webhooks salientes | ✅ Implementado | Core | `RuleEngine` determinista con HMAC |
| Modelo de dominio de factura estructurado (`StructuredInvoice`) | ✅ Implementado | Luis (P1) | `InvoiceStructurizer` con normalización difusa |
| Persistencia de `DocumentCheck`, `EntityRecord`, `InvoiceFingerprint` | ✅ Implementado | Luis (P1) | Tablas en BD y migración Alembic |
| Endpoints REST de revisión (`/documents`, `/decision/checks`, `/review`) | ✅ Implementado | Luis (P2) | Respuestas tipadas con `check_summary` |
| App de gestión financiera nativa (`PySide6 / Qt6`) | ✅ Implementado | Brandon (P3) | UI navegable, KPIs, badges de severidad, auditoría y 13 tests en verde |
| Instalador y lanzador unificado multiplataforma | ✅ Implementado | Brandon (P3) | `install.py` y `start.py` (100% Python) |
| Retiro de frontend web obsoleto y dependencias Node.js | ✅ Ejecutado | Equipo | Alineado con ADR-003 |
| Hot-folder conectado al backend con API Key | ⏳ En progreso | Beatriz (P4a) | `tray_agent.py` enviando a `/upload` |
| Pantalla de configuración del agente (`SettingsView`) | ⏳ En progreso | Beatriz (P4a) | Formulario de carpetas y API Key |
| Integración final y orquestación del vertical completo | ⏳ Pendiente | Hector (P4b) | Validación global y cierre |

---

## 4. Decisiones Ejecutadas

1. **Cliente oficial = Suite de escritorio PySide6** (`ADR-003`). El frontend web Next.js fue **removido por completo del repositorio**.
2. **Validadores conectados al pipeline**: las facturas procesadas alimentan el structurizer, validación matemática, Sentinel y persistencia de hallazgos.
3. **Pila 100% Python**: eliminación total de Node.js y npm, simplificando el entorno de desarrollo y ejecución.
4. **Instalación y arranque deterministas**: scripts `install.py` y `start.py` con autodetección de plataforma (Windows/Linux) y asignación automática de puertos.

---

## 5. Referencias

* PRD del producto: [`docs/01-product/01-prd.md`](01-prd.md)
* Roadmap y estado de componentes: [`docs/03-roadmap.md`](03-roadmap.md)
* TDD del vertical (dominio, pipeline, API, escritorio, automatización): [`docs/04-engineering/04-invoice-validation-review.md`](../04-engineering/04-invoice-validation-review.md)
* Decisión de migración UI: [`docs/09-decisions/ADR-003-desktop-first-ui.md`](../09-decisions/ADR-003-desktop-first-ui.md)
* División de trabajo en 4 personas: [`docs/08-operations/02-trabajo-equipo-proyecto4.md`](../08-operations/02-trabajo-equipo-proyecto4.md)