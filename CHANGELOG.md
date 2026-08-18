# Changelog — FlowMind AI

Todas las modificaciones notables realizadas en el proyecto FlowMind AI se documentan en este archivo conforme al estándar obligatorio establecido en `documentation` skill.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

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
