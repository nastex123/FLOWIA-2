# Changelog — FlowMind AI

Todas las modificaciones notables realizadas en el proyecto FlowMind AI se documentan en este archivo conforme al estándar obligatorio establecido en `documentation` skill.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

### [2026-08-18 14:10] (America/Bogota)

- **[Docs / Governance]** Inclusión de directiva obligatoria y advertencia al inicio del `README.md`
  - **Qué:** Inclusión de una alerta `> [!IMPORTANT]` en la cabecera de `README.md` que instruye a desarrolladores y agentes de IA a leer obligatoriamente toda la documentación en `docs/`, `AGENTS.md`, `GEMINI.md` y todas las skills del repositorio (`skills/documentation/`, `skills/flowmind-development/`, `skills/technical-partner/`) antes de realizar modificaciones.
  - **Por qué:** Garantizar que cualquier colaborador o agente de IA mantenga la consistencia arquitectónica, el tipado estricto, la privacidad local y la sincronización continua de la documentación.
  - **Archivos:** `README.md`, `CHANGELOG.md`.

---

### [2026-08-18 14:05] (America/Bogota)

- **[Docs / Project]** Sincronización integral de la documentación técnica (`docs/`), estado de avance y consolidación de tareas
  - **Qué:** 
    - `docs/01-product/03-roadmap.md`: actualizada la Fase 3 con la entrega completa de la Suite de Escritorio PySide6 (UI de gestión financiera, KPIs, visor en 2 columnas, badges de severidad, revisión y tests), actualizada la Fase 8 (agente de bandeja e instalador `install.py`) y Fase 10 (persistencia de `document_checks`, `entity_records`, `invoice_fingerprints`).
    - `docs/01-product/04-proyecto4-alineacion-tarea.md`: actualizada la matriz de brechas y decisiones ejecutadas, reflejando la resolución del dominio de factura estructurada, endpoints de revisión y la UI de escritorio.
    - `docs/03-architecture/01-general-architecture.md`: actualizado el diagrama Mermaid global eliminando el nodo web y consolidando la arquitectura cliente-servidor 100% nativa en Python.
    - `docs/08-operations/02-trabajo-equipo-proyecto4.md`: actualizada la tabla de criterios de finalización con el estado real de cada persona (Brandon P3 completado al 100%, Luis P1+P2 completado al 100%, Beatriz P4a en progreso y Hector P4b pendiente de integración final).
  - **Por qué:** Mantener `docs/` como la fuente de verdad técnica y arquitectónica del proyecto, asegurando trazabilidad exacta entre el código implementado, los entregables de cada integrante del equipo y las fases pendientes.
  - **Archivos:** `docs/01-product/03-roadmap.md`, `docs/01-product/04-proyecto4-alineacion-tarea.md`, `docs/03-architecture/01-general-architecture.md`, `docs/08-operations/02-trabajo-equipo-proyecto4.md`, `CHANGELOG.md`.

---

### [2026-08-18 13:56] (America/Bogota)

- **[Architecture / Cleanup]** Eliminación del frontend web (Next.js) y consolidación 100% en la Suite de Escritorio Nativa (PySide6 / Qt6)
  - **Qué:** 
    - `frontend/`: eliminado el directorio completo y todos los archivos del andamiaje web roto de Next.js (`package.json`, `tsconfig.json`, `src/`, `next.config.js`).
    - `scripts/start_frontend.ps1`: eliminado.
    - `backend/app/core/config.py`: actualizado `ALLOWED_ORIGINS` por defecto a `["*"]` para clientes locales de escritorio y API.
    - `install.py`: simplificado para enfocarse 100% en Python, eliminando verificaciones de Node.js/npm y el paso de `npm install`.
    - `start.py`: eliminado el flag `--web` y el subproceso Next.js, consolidando el lanzador en Backend FastAPI + Suite de Escritorio PySide6.
    - `.gitignore`, `.env.example`, `.env`, `README.md`, `AGENTS.md`, `GEMINI.md`, `docs/09-decisions/ADR-003-desktop-first-ui.md`: actualizados para reflejar que el stack es 100% Python y que la suite de escritorio es el único cliente de usuario.
  - **Por qué:** Cumplir con la decisión arquitectónica ADR-003, eliminar deuda técnica innecesaria de Node.js/npm y enfocar todos los esfuerzos del equipo en la GUI de escritorio nativa PySide6.
  - **Archivos:** `frontend/` (eliminado), `scripts/start_frontend.ps1` (eliminado), `backend/app/core/config.py`, `install.py`, `start.py`, `.gitignore`, `.env.example`, `.env`, `README.md`, `AGENTS.md`, `GEMINI.md`, `docs/09-decisions/ADR-003-desktop-first-ui.md`, `CHANGELOG.md`.

---

### [2026-08-18 13:49] (America/Bogota)

- **[Tooling / Scripts]** Creación del instalador automatizado multiplataforma `install.py` y actualización del `README.md`
  - **Qué:** 
    - `install.py`: nuevo script de configuración automática y multiplataforma (Windows, Linux y macOS) sin dependencias externas. Detecta el sistema operativo, valida Python 3.11+, Git y Node.js/npm, crea el entorno virtual `venv`, actualiza `pip`, instala el paquete backend en modo editable con extras `[dev]` (`pip install -e "./backend[dev]"`), copia y configura `.env` para SQLite local out-of-the-box, ejecuta `npm install` en el frontend, y realiza un *Smoke Test* de 9 módulos críticos (`fastapi`, `pydantic v2`, `sqlalchemy`, `pandas`, `pymupdf`, `sklearn`, `opencv`, `pyside6`, `networkx`). Incluye soporte para banderas `--os windows`, `--os linux`, `--backend-only`, `--frontend-only` y `--skip-smoke-test`.
    - `README.md`: actualizado para presentar `python install.py` como la opción recomendada de instalación rápida con un solo comando.
  - **Por qué:** Eliminar fricciones de instalación y garantizar que cualquier desarrollador configure y verifique el entorno de desarrollo completo de forma determinista y reproducible con un solo comando.
  - **Archivos:** `install.py`, `README.md`, `CHANGELOG.md`.

---

### [2026-08-18 13:35] (America/Bogota)

- **[Docs / Config]** Actualización integral del `README.md` y guía de instalación clara paso a paso
  - **Qué:** 
    - `README.md`: reestructuración y formateo exhaustivo de la documentación de inicio rápido, agregando bloques de código explícitos con sintaxis para Windows PowerShell, Windows CMD y Linux/macOS Bash, guía completa y matriz comparativa de variables de entorno para Windows vs Linux (rutas, SQLite vs PostgreSQL, Redis, S3), ejemplos de definición temporal en terminal (`$env:VAR`, `set VAR`, `export VAR`), tabla de credenciales por defecto, opciones de ejecución unificada (`start.py`, `start.ps1`, `start.sh`), banderas CLI (`--web`, `--no-ui`), ejecución de pruebas con `pytest` y generación de datos de prueba (`samples/`).
    - `.env.example`: enriquecido con secciones separadas, comentarios explicativos para Windows y Linux, y valores por defecto para SQLite local y PostgreSQL/Docker.
    - `.env`: configurado por defecto para SQLite asíncrono en modo local, permitiendo ejecución y tests inmediatos sin dependencia forzosa de Docker/PostgreSQL.
  - **Por qué:** Asegurar que cualquier desarrollador en Windows o Linux configure correctamente sus variables de entorno, rutas relativas/absolutas y dependencias sin errores de conexión o formato.
  - **Archivos:** `README.md`, `.env.example`, `.env`, `CHANGELOG.md`.

---

### [2026-08-18 11:48] (America/Bogota)

- **[Desktop / Launcher]** Integración de UI en `start.py`, asignación dinámica de puertos libres, modernización visual del diseño y auto-login fluido
  - **Qué:** 
    - `start.py`: actualizado para detectar puertos ocupados (evitando `[Errno 98] Address already in use`), encontrar automáticamente el primer puerto libre (ej. `8001`), iniciar Uvicorn y lanzar la suite de escritorio PySide6 (`desktop/main.py --api-url=http://127.0.0.1:<puerto>`), con apagado coordinado (*graceful shutdown*).
    - `desktop/main.py`: soporte de argumento `--api-url` y variable de entorno `FLOWMIND_API_URL` para enlace dinámico y transparente con el backend.
    - `desktop/ui/styles.py`: nuevo sistema de diseño y temas visuales Dark Theme moderno (paleta Slate, bordes sutiles, micro-contrastes y componentes consistentes).
    - `desktop/ui/login_dialog.py`: rediseño visual con botón de acceso directo a "Modo Demo Offline", auto-login al pulsar Enter/Aceptar y detección de backend no disponible.
    - `desktop/ui/documents_view.py`: añadidas tarjetas de métricas KPIs (Total, Críticas, Advertencias, Revisadas) y barra de búsqueda en tiempo real.
    - `desktop/ui/invoice_review_view.py`: rediseño en layout de 2 columnas fluidas con divisor `QSplitter`, tarjetas de cabecera y panel de auditoría destacado.
  - **Por qué:** Permitir al usuario ejecutar la aplicación completa con un solo comando (`python3 start.py`) y ofrecer una experiencia de usuario atractiva, moderna y sin fricciones de inicio de sesión o colisiones de puertos.
  - **Archivos:** `start.py`, `desktop/main.py`, `desktop/ui/styles.py`, `desktop/ui/login_dialog.py`, `desktop/ui/main_window.py`, `desktop/ui/documents_view.py`, `desktop/ui/invoice_review_view.py`, `CHANGELOG.md`.

---

### [2026-08-18 11:22] (America/Bogota)

- **[Desktop / Frontend]** Implementación completa de la UI de Gestión Financiera en PySide6 (P3 — Brandon)
  - **Qué:** Se finalizó y validó la interfaz de escritorio de revisión financiera:
    - `desktop/controllers/api_client.py`: métodos completos del contrato (`login`, `me`, `list_documents`, `get_document`, `list_checks`, `review_document`, `upload_file`).
    - `desktop/ui/login_dialog.py`: diálogo de autenticación JWT (con selector de organización) y soporte para modo API Key.
    - `desktop/ui/main_window.py`: arquitectura de navegación `QStackedWidget` con Facturas, Detalle, Configuración (carga perezosa de `SettingsView` de P4) y Modo Local.
    - `desktop/ui/documents_view.py`: vista de comprobantes con badges coloreados de severidad de anomalías (`critical`, `warning`, `info`, `ok`) y doble clic a detalle.
    - `desktop/ui/invoice_review_view.py`: detalle de factura estructurada (cabecera, tabla de ítems, resumen de impuestos y totales), panel de hallazgos (`document_checks`) y acción "Marcar como revisada".
    - `tests/test_desktop_invoice_review.py`: 13 pruebas automatizadas cubriendo el contrato simulado TDD §5 y la integración directa con el backend FastAPI.
  - **Por qué:** Cumplir con los entregables de la persona 3 (Brandon) definidos en `docs/08-operations/02-trabajo-equipo-proyecto4.md` y `docs/04-engineering/04-invoice-validation-review.md`.
  - **Archivos:** `desktop/controllers/api_client.py`, `desktop/controllers/mock_backend.py`, `desktop/ui/main_window.py`, `desktop/ui/documents_view.py`, `desktop/ui/invoice_review_view.py`, `desktop/ui/login_dialog.py`, `tests/test_desktop_invoice_review.py`, `CHANGELOG.md`.

---

### [2026-08-18 10:35] (America/Bogota)

- **[CI]** Fix de tests de escritorio (PySide6) en GitHub Actions headless
  - **Qué:** Se configuró el CI para soportar Qt sin pantalla: se añadió `QT_QPA_PLATFORM=offscreen` al entorno del job y un paso que instala las librerías de sistema de Qt (`libegl1`, `libgl1`, `libxkbcommon0`, `libdbus-1-3`) en `.github/workflows/ci.yml`. En `tests/conftest.py` se fija `QT_QPA_PLATFORM=offscreen` por defecto antes de importar Qt, para que los tests de escritorio pasen también en máquinas headless locales.
  - **Por qué:** `pytest tests/` fallaba en el runner de GitHub Actions con `ImportError: libEGL.so.1` porque PySide6 es dependencia del backend y los tests de escritorio crean un `QApplication` sin librerías gráficas de sistema instaladas.
  - **Archivos:** `.github/workflows/ci.yml`, `tests/conftest.py`, `CHANGELOG.md`.

---

### [2026-08-18 10:10] (America/Bogota)

- **[Docs]** Asignación definitiva del equipo a la división de trabajo del Proyecto 4
  - **Qué:** Se asignaron los integrantes del equipo a cada tarea en `docs/08-operations/02-trabajo-equipo-proyecto4.md`: **Brandon** (P3 — Frontend / App de Escritorio PySide6, a cargo de la UI), **Luis** (P1 + P2 — Backend total: Backend Core y API de Revisión), **Beatriz** (P4 — Automatización Hot-Folder / agente de bandeja) y **Hector** (P4 — Integración final y coordinación / orquestador). La tarea P4 quedó dividida en dos responsables con pasos y criterios de finalización propios. Se actualizaron el mapa de personas, encabezados, contratos de interfaz, secuencia/dependencias y criterios de finalización con los nombres.
  - **Por qué:** El equipo definió los integrantes reales; Brandon queda a cargo del frontend y Luis a cargo de todo el backend, repartiéndose la automatización e integración Beatriz y Hector.
  - **Archivos:** `docs/08-operations/02-trabajo-equipo-proyecto4.md`, `CHANGELOG.md`.

---

### [2026-08-18 08:27] (America/Bogota)

- **[Docs]** Ajuste de la división de trabajo del Proyecto 4 de 3 a 4 personas
  - **Qué:** Se reescribió `docs/08-operations/02-trabajo-equipo-proyecto4.md` para dividir la implementación en 4 personas (P1 Backend Core, P2 Backend API de Revisión, P3 App de Escritorio UI, P4 Automatización Hot-Folder + Integración), especificando la **tarea exacta y los pasos a seguir** de cada una, contratos de interfaz y criterios de finalización. Se actualizaron las referencias a "3 personas" en `README.md`, `docs/09-decisions/ADR-003-desktop-first-ui.md` y `docs/01-product/04-proyecto4-alineacion-tarea.md`.
  - **Por qué:** El equipo amplió su número de integrantes a 4; la división anterior concentraba toda la parte de escritorio en una sola persona.
  - **Archivos:** `docs/08-operations/02-trabajo-equipo-proyecto4.md`, `README.md`, `docs/09-decisions/ADR-003-desktop-first-ui.md`, `docs/01-product/04-proyecto4-alineacion-tarea.md`, `CHANGELOG.md`.

---

### [2026-08-18 08:13] (America/Bogota)

- **[Docs]** Documentación previa del Proyecto 4 — Extractor, Validador y Reconciliador de Facturas y Comprobantes
  - **Qué:** Se creó el paquete documental previo a la implementación: (1) alineación de la tarea asignada con el proyecto y análisis de brechas; (2) TDD del vertical completo (dominio `StructuredInvoice`, pipeline de validación, modelo de datos con `document_checks`/`entity_records`/`invoice_fingerprints`, contratos de API de revisión, app de escritorio PySide6 y flujo hot-folder→backend); (3) ADR-003 (cliente principal en PySide6 con frontend web deprecated); (4) división del trabajo en 4 personas con contratos de interfaz. Se actualizó el índice de documentación de `README.md` y se marcó `frontend/README.md` como deprecated.
  - **Por qué:** La tarea asignada exige coordinar a 4 personas sobre un vertical completo; la documentación es la fuente de verdad del proyecto y debe definirse y acordarse antes de escribir código (regla de `documentation` skill).
  - **Archivos:** `docs/01-product/04-proyecto4-alineacion-tarea.md`, `docs/04-engineering/04-invoice-validation-review.md`, `docs/09-decisions/ADR-003-desktop-first-ui.md`, `docs/08-operations/02-trabajo-equipo-proyecto4.md`, `README.md`, `frontend/README.md`, `CHANGELOG.md`.

---

### [2026-08-17 19:44] (America/Bogota)

- **[Docs]** Eliminación de archivos planos obsoletos en la raíz de `docs/` y migración completa a la jerarquía formal
  - **Qué:** Se eliminaron los 11 archivos Markdown planos que residían en la raíz de `docs/` (`01-architecture.md`, `02-mvp-roadmap.md`, `03-schemas-and-mapping.md`, `04-api-reference.md`, `05-desktop-pyside6.md`, `06-advanced-engines.md`, `07-local-search-and-compliance.md`, `08-enterprise-decision-engine.md`, `09-database-migrations.md`, `10-expansion-proposals.md`, `11-security.md`) tras migrar y reorganizar todo su contenido técnico en las carpetas temáticas del estándar:
    - `docs/00-vision/` (Visión)
    - `docs/01-product/` (PRD, Esquemas y Roadmap)
    - `docs/03-architecture/` (Arquitectura general, Decision Engine y PySide6 Desktop)
    - `docs/04-engineering/` (API Reference, Database Alembic y Advanced Engines)
    - `docs/05-ai/` (Arquitectura de IA y ML local)
    - `docs/06-security/` (Seguridad, Privacidad y Cumplimiento SII/PII)
    - `docs/08-operations/` (Propuestas de expansión futura)
    - `docs/09-decisions/` (ADRs 001 y 002)
    Se actualizó el índice maestro en [`README.md`](README.md).
  - **Por qué:** Cumplir estrictamente con la regla de estructura jerárquica obligatoria de `documentation` skill, eliminando duplicidades y fuentes contradictorias de verdad en el repositorio.
  - **Archivos:** `docs/*` (directorios temáticos), [`README.md`](README.md), [`CHANGELOG.md`](CHANGELOG.md).

---

### [2026-08-17 19:32] (America/Bogota)

- **[Docs]** Reestructuración integral de la documentación según el nuevo estándar formal de Documentation Skill
  - **Qué:** Se actualizó la skill `documentation` con el nuevo estándar de 20 reglas y se crearon los directorios y documentos maestros correspondientes.
  - **Por qué:** Asegurar que el repositorio cuente con trazabilidad completa entre Visión, PRD, Arquitectura, IA, Decisiones (ADRs) y Propuestas.
  - **Archivos:** [`docs/00-vision/01-vision.md`](docs/00-vision/01-vision.md), [`docs/01-product/01-prd.md`](docs/01-product/01-prd.md), [`docs/05-ai/01-local-ai-architecture.md`](docs/05-ai/01-local-ai-architecture.md), [`docs/09-decisions/ADR-001-local-deterministic-engine.md`](docs/09-decisions/ADR-001-local-deterministic-engine.md), [`docs/09-decisions/ADR-002-two-plane-architecture.md`](docs/09-decisions/ADR-002-two-plane-architecture.md), [`CHANGELOG.md`](CHANGELOG.md).

---

### [2026-08-17 19:26] (America/Bogota)

- **[Docs]** Creación del documento maestro de propuestas estratégicas y actualización del índice
  - **Qué:** Se formalizaron 22 propuestas de alto impacto técnico y comercial divididas en 6 bloques temáticos.
  - **Por qué:** Registrar la visión de expansión del producto solicitada durante la fase de planificación y documentación.
  - **Archivos:** [`docs/08-operations/01-expansion-proposals.md`](docs/08-operations/01-expansion-proposals.md), [`README.md`](README.md).

---

### [2026-08-17 19:18] (America/Bogota)

- **[Docs]** Sincronización y pulido integral de la documentación técnica y arquitectónica
  - **Qué:** Se actualizaron y documentaron los endpoints de los routers activos `/api/v1/decision`, `/api/v1/business` y `/api/v1/compliance`.
  - **Por qué:** Eliminar el desfase detectado entre el código implementado y la documentación técnica de referencia.
  - **Archivos:** `docs/`
