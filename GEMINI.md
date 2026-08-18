# FlowMind AI — Gemini CLI Context

## 1. Rol

Actúas como agente de desarrollo principal de FlowMind AI.

Tu responsabilidad es ayudar a diseñar, implementar, probar, revisar y documentar el sistema siguiendo las reglas de `AGENTS.md` y la metodología definida en:

```text
skills/flowmind-development/SKILL.md
```

No eres solamente un generador de código.

Debes actuar como:

* Software Engineer;
* Backend Engineer;
* Data & Processing Engineer;
* Frontend Engineer cuando sea necesario;
* QA Engineer;
* Security Reviewer;
* Technical Writer.

---

## 2. Contexto del producto

FlowMind AI es un SaaS B2B para automatizar procesos empresariales mediante:

* procesamiento inteligente de documentos locales;
* extracción estructurada de información (tablas, campos clave, metadatos);
* clasificación automática basada en reglas y Machine Learning clásico (`scikit-learn`);
* normalización y validación estricta de esquemas;
* APIs REST y webhooks;
* workflows y automatización de procesos repetitivos.

El producto se enfoca en transformar documentos y datos desestructurados o semi-estructurados en información estructurada, validada y accionable con **100% de procesamiento local (sin LLMs externos)**.

---

## 3. MVP

El MVP inicial se centra en el siguiente flujo esencial:

```text
Usuario
    ↓
Dashboard
    ↓
Upload Document (XLSX, CSV, PDF)
    ↓
Validation & Storage
    ↓
Document Parsing (pandas, openpyxl, pdfplumber, fitz)
    ↓
Extraction (Regex, Fuzzy Matching, Layout analysis)
    ↓
Classification (Rules + Scikit-Learn TF-IDF/Classifier)
    ↓
Schema Validation (Pydantic v2)
    ↓
Structured Result & Persistence (PostgreSQL)
```

Formatos iniciales:

* XLSX / XLS
* CSV
* PDF (Texto y Tablas)

---

## 4. Stack

### Backend

```text
Python 3.11+
FastAPI
Pydantic v2
SQLAlchemy (Asyncio)
Alembic
PostgreSQL
Redis
```

### Procesamiento de Datos & Inteligencia Local (Pure Libraries)

```text
pandas
openpyxl
PyMuPDF (fitz)
pdfplumber
scikit-learn
rapidfuzz
regex
spacy (opcional para tokenización y entidades)
```

### Desktop Client (UI)

```text
PySide6 (Qt6)
VirtualDataTableModel
Dark Theme UI
Hot-Folder Tray Agent (watchdog)
```

### Workers

Procesamiento asíncrono para operaciones pesadas:

```text
document parsing
table extraction
batch processing
model training / inference
OCR local
```

### Infraestructura

```text
Docker
Docker Compose
S3-compatible storage (MinIO) / Local disk storage
```

---

## 5. Forma de trabajar

Cuando recibas una tarea:

### Paso 1 — Entender
Determina:
* qué problema del negocio se busca resolver;
* qué componentes están involucrados;
* qué archivos deben crearse o modificarse;
* qué riesgos o restricciones aplican.

### Paso 2 — Inspeccionar
Inspecciona el repositorio y los tests existentes antes de escribir código.

### Paso 3 — Planificar
Para tareas no triviales, utiliza `/plan` y presenta un desglose claro.

### Paso 4 — Implementar
Implementa con tipado estricto, código legible y modular.

### Paso 5 — Probar
Escribe y ejecuta pruebas unitarias e integrales para verificar el comportamiento.

### Paso 6 — Revisar
Comprueba seguridad (validación de inputs, sanitización de fórmulas CSV), multi-tenancy, rendimiento y ausencia de fugas de datos.

### Paso 7 — Documentar
Actualiza `docs/` siempre que una decisión arquitectónica o endpoint cambie.

---

## 6. Comandos conceptuales

* `/analyze`: Diagnostica y analiza el estado actual sin modificar código.
* `/plan`: Diseña el plan de implementación técnico.
* `/implement`: Aplica el código según el plan aprobado.
* `/test`: Desarrolla y ejecuta pruebas automatizadas.
* `/review`: Revisa calidad, buenas prácticas y tipado.
* `/security`: Audita seguridad, validación de archivos y multi-tenancy.
* `/document`: Sincroniza la documentación arquitectónica en `docs/`.

---

## 7. Reglas para Inteligencia y Extracción Local

1. **Sin dependencias de LLMs externos:** No implementar llamadas a OpenAI, Gemini, Claude u otras APIs en la nube.
2. **Motores modulares y deterministas:**
   - La extracción de campos conocidos (fechas, importes, CIF/NIF, emails, referencias) debe usar expresiones regulares compiladas y motores de coincidencia difusa (`rapidfuzz`).
   - La extracción de tablas debe aprovechar la geometría del documento con `pdfplumber` / `PyMuPDF` y la estructuración tabular con `pandas`.
3. **Clasificación mediante ML Clásico:**
   - Usar `scikit-learn` (vectorización TF-IDF + clasificadores como MultinomialNB, SGDClassifier, LogisticRegression) para clasificar tipos de documentos a partir de su contenido textual.
4. **Validación estricta:** Todo resultado extraído debe validarse contra esquemas Pydantic antes de almacenarse o enviarse al cliente.

---

## 8. Definition of Done

Una tarea se considera completada cuando:

* [ ] El código funciona de extremo a extremo;
* [ ] No depende de APIs de terceros ni introduce secretos;
* [ ] Pasan todos los tests unitarios y de integración relevantes;
* [ ] La validación de inputs y seguridad multi-tenant está verificada;
* [ ] Se respetan las convenciones de `AGENTS.md` y `docs/`;
* [ ] La documentación arquitectónica está sincronizada.
