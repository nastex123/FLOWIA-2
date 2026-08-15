# 02 — Roadmap de Desarrollo del MVP

Este documento define las fases de entrega incremental para el **MVP de FlowMind AI**.

---

## Objetivo del MVP

Construir un flujo robusto de extremo a extremo que permita a un usuario corporativo subir un archivo (Excel, CSV o PDF), procesarlo localmente mediante librerías de Python sin APIs externas, extraer su estructura y datos clave de forma confiable, y visualizar los resultados en una interfaz limpia.

---

## Fases de Implementación

### Fase 1: Cimientos y Procesamiento Local (Actual)
- [x] Establecer gobernanza, reglas de agentes y arquitectura (`AGENTS.md`, `GEMINI.md`, `SKILL.md`, `docs/`).
- [ ] Implementar motor base de extracción tabular (`pandas`, `openpyxl`, `csv`).
- [ ] Implementar motor base de extracción PDF (`PyMuPDF`, `pdfplumber`).
- [ ] Implementar motor de reglas y extracción de entidades (`regex`, `rapidfuzz`).
- [ ] Implementar clasificador de documentos clásico con `scikit-learn`.
- [ ] Crear suite de pruebas unitarias exhaustivas para casos borde.

### Fase 2: Backend API & Persistencia
- [ ] Configurar modelos SQLAlchemy (`Organization`, `User`, `Document`, `ExtractionJob`, `ExtractedData`).
- [ ] Configurar migraciones con Alembic.
- [ ] Implementar endpoints REST para carga de archivos, estado de procesamiento y consulta de resultados.
- [ ] Implementar autenticación JWT y middleware multi-tenant.

### Fase 3: Procesamiento Asíncrono con Workers
- [ ] Orquestación de colas en Redis para tareas pesadas.
- [ ] Gestión de estados del trabajo (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`).
- [ ] Mecanismos de reintentos e idempotencia.

### Fase 4: Frontend Dashboard
- [ ] Interfaz de carga de documentos con drag-and-drop y feedback visual.
- [ ] Tabla interactiva para previsualizar y editar datos extraídos.
- [ ] Filtros por tipo de documento y estado de validación.

### Fase 5: Reglas de Mapeo Personalizadas & Exportación
- [ ] Definición de esquemas de datos por organización (JSON schema / mapeador de columnas).
- [ ] Exportación a CSV normalizado, Excel y webhook externo.
