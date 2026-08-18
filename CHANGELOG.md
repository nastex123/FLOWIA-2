# Changelog — FlowMind AI

Todas las modificaciones notables realizadas en el proyecto FlowMind AI se documentan en este archivo conforme al estándar obligatorio establecido en `documentation` skill.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

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
