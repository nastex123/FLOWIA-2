---
name: flowmind-development
description: Metodología especializada para desarrollar FlowMind AI como un SaaS B2B de automatización inteligente basado puramente en librerías locales de Python y modelos clásicos de ML (sin LLMs externos). Utilizar para analizar, planificar, implementar, probar, revisar y documentar funcionalidades del proyecto.
---

# FlowMind Development Skill

## Propósito

Esta skill define cómo debe trabajar un agente de IA cuando desarrolla **FlowMind AI**.

El objetivo es mantener una metodología consistente entre:

* arquitectura;
* backend (FastAPI + Pydantic v2 + SQLAlchemy Async);
* frontend (Next.js + TypeScript);
* procesamiento de documentos (pandas, openpyxl, pdfplumber, PyMuPDF);
* inteligencia local (scikit-learn, rapidfuzz, regex, spaCy);
* workers asíncronos (Redis);
* base de datos multi-tenant (PostgreSQL);
* seguridad y privacidad de datos;
* testing integral;
* documentación arquitectónica.

---

# 1. Mentalidad

Trabaja como un equipo senior de ingeniería construyendo un producto SaaS comercial robusto, privado y rápido.

Prioridades:

```text
Privacidad & Seguridad (Zero Cloud Data Leakage)
↓
Correctitud
↓
Mantenibilidad
↓
Rendimiento & Latencia
↓
Testing
↓
Escalabilidad
```

No sacrificar correctitud ni seguridad por velocidad de entrega.

---

# 2. Análisis & Extracción sin LLMs

Para cualquier tarea de procesamiento documental:

### 1. Ingesta & Validación
* Inspeccionar cabeceras binarias (MIME real).
* Validar tamaño máximo para prevenir saturación de memoria.
* Sanitizar hojas de cálculo para prevenir *CSV/Excel Formula Injection*.

### 2. Parsing Local
* Para **CSV**: Detección inteligente de delimitadores (`csv.Sniffer`), encoding (UTF-8, Latin-1) y carga streaming/lotes con `pandas`.
* Para **XLSX**: Manejo de hojas múltiples con `openpyxl` / `pandas`, identificación de filas vacías y tipos de celdas heterogéneos.
* Para **PDF**: Extracción de capas de texto con `PyMuPDF` (`fitz`) y detección de rejillas/tablas tabulares con `pdfplumber`.

### 3. Extracción & Matching Difuso
* Usar `regex` compilados para campos normalizables (fechas ISO/locales, NIF/CIF, emails, importes monetarios, números de factura).
* Usar `rapidfuzz` para asociar columnas desestructuradas con esquemas canónicos de datos (ej. "Val. Total", "Importe Total", "Total Bruto" -> `total_amount`).

### 4. Clasificación con Machine Learning Clásico
* Pipelines de `scikit-learn`: `TfidfVectorizer` + `LogisticRegression` / `MultinomialNB`.
* Reglas heurísticas rápidas combinadas con modelos supervisados ligeros.

### 5. Validación Tipada
* Todos los datos extraídos se convierten en modelos `Pydantic v2` para garantizar tipos de datos correctos antes de la persistencia.

---

# 3. Arquitectura del Backend

Separación estricta de responsabilidades:

```text
app/
├── api/            # Rutas FastAPI, inyección de dependencias, autenticación
├── core/           # Configuración (Pydantic Settings), logging, excepciones
├── domain/         # Modelos de dominio y Schemas Pydantic (Request/Response)
├── infrastructure/ # Modelos SQLAlchemy, sesiones async, clientes S3/Local
└── services/       # Lógica de negocio, parsers, extractores y clasificadores
    ├── extractors/
    └── classifiers/
```

Los endpoints no deben contener lógica de extracción ni consultas SQL directas; deben delegar a la capa de servicios.

---

# 4. Multi-tenancy

Toda consulta a la base de datos debe estar vinculada explícitamente a un tenant (`organization_id`).

```python
# Ejemplo conceptual correcto
async def get_document(db: AsyncSession, doc_id: UUID, org_id: UUID) -> Document | None:
    stmt = select(Document).where(Document.id == doc_id, Document.organization_id == org_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
```

---

# 5. Definition of Done

Antes de dar por concluida una tarea:

* [ ] Código implementado con tipado completo (`typing` en Python / TypeScript en frontend).
* [ ] Sin llamadas a APIs externas de IA en la nube.
* [ ] Tests automatizados pasando con casos representativos y casos límite.
* [ ] Sin secretos en el repositorio ni variables hardcodeadas.
* [ ] Manejo explícito de excepciones sin `except Exception: pass`.
* [ ] Documentación en `docs/` actualizada si hubo cambios arquitectónicos.
