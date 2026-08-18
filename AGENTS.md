# AGENTS.md

## FlowMind AI — Repository Development Guidelines

Este documento define las reglas generales que cualquier agente de IA debe seguir al trabajar en el repositorio de FlowMind AI.

El agente debe considerar este archivo como un conjunto de restricciones de desarrollo, calidad y arquitectura.

---

## 1. Objetivo del proyecto

FlowMind AI es una plataforma SaaS B2B orientada a la automatización inteligente de procesos empresariales.

El sistema busca transformar información desestructurada o semi-estructurada proveniente de:

* Excel (XLSX, XLS)
* CSV
* PDF (tablas, formularios, texto plano)
* correos electrónicos
* formularios
* APIs
* webhooks

en información estructurada, validada y acciones automatizadas.

El objetivo comercial es reducir trabajo manual, errores operativos y tiempo empleado en procesos repetitivos, garantizando máxima privacidad de datos, velocidad y determinismo.

---

## 2. Principios fundamentales

### 2.1 Resolver problemas reales

No implementar funcionalidades únicamente porque sean técnicamente interesantes.

Cada funcionalidad debe responder a una necesidad concreta del producto, del usuario o de la arquitectura.

### 2.2 Simplicidad antes que sobreingeniería

Preferir:

* soluciones simples;
* componentes pequeños;
* interfaces claras;
* dependencias justificadas;
* arquitectura incremental.

No introducir sistemas distribuidos, microservicios o tecnologías adicionales sin una razón concreta.

### 2.3 Seguridad y Privacidad por defecto (Zero Cloud Data Leakage)

Nunca:

* hardcodear API keys o credenciales;
* almacenar secretos en el repositorio;
* registrar información sensible innecesariamente;
* confiar en datos proporcionados por el usuario;
* ejecutar archivos subidos sin validación estricta;
* enviar datos confidenciales a servicios o APIs de terceros en la nube sin autorización explícita.

Utilizar variables de entorno y mecanismos adecuados de gestión de secretos.

### 2.4 Código mantenible

El código debe:

* ser legible;
* tener nombres descriptivos;
* utilizar tipado estricto (Type hints en Python);
* separar responsabilidades;
* evitar duplicación innecesaria;
* tener funciones pequeñas y enfocadas.

### 2.5 Estilo y Comunicación (Cero Emojis)

El agente debe comunicarse de forma sobria, técnica y formal:

* No utilizar emojis en respuestas, planes de ejecución, explicaciones ni mensajes.
* No utilizar emojis en nombres de variables, funciones, clases, archivos o tests.
* No utilizar emojis en mensajes de commit ni entradas de CHANGELOG.md.
* No utilizar emojis en etiquetas o botones de interfaces de usuario.

---

## 3. Arquitectura

La arquitectura contempla la siguiente separación:

```text
frontend/
backend/
workers/
infrastructure/
tests/
docs/
skills/
```

La separación de responsabilidades debe mantenerse.

### Backend

Responsable de:

* API REST (FastAPI);
* autenticación y autorización;
* validación y esquemas Pydantic;
* lógica de negocio y orquestación;
* persistencia en base de datos;
* integración con almacenamiento local o S3.

### Workers

Responsables de operaciones potencialmente largas y asíncronas:

* procesamiento y parsing de documentos pesados;
* extracción de entidades y tablas;
* OCR local;
* clasificación y ejecución de modelos de Machine Learning tradicionales;
* tareas en segundo plano.

### Frontend Web Suite (UI)

Responsable de:

* interfaz de usuario web moderna, reactiva y de alta velocidad (Next.js 14+ / React / TypeScript / Tailwind CSS);
* interacción fluida con usuarios y visualización en tiempo real en navegador (`http://localhost:3000`);
* revisión estructurada de facturas y auditoría de anomalías;
* monitor y visualización de ingestas y estado de la cripta local;
* configuración de conexiones y selector de organizaciones.

---

## 4. Tecnologías objetivo

El stack objetivo se basa en tecnologías sólidas, escalables y de ejecución local:

### Backend

* Python 3.11+
* FastAPI
* Pydantic v2
* SQLAlchemy (Asyncio)
* Alembic
* PostgreSQL (con extensiones necesarias) / SQLite Local Asíncrono
* Redis

### Procesamiento de Documentos e Inteligencia Local (Pure Libraries)

* **Tabular & Hojas de cálculo:** `pandas`, `openpyxl`, `csv`
* **PDFs & Documentos:** `PyMuPDF` (`fitz`), `pdfplumber`
* **NLP & Extracción por Patrones:** `spacy`, `regex`, `rapidfuzz` (fuzzy matching de encabezados y aliases), `nltk`
* **Machine Learning Clásico & Clasificación:** `scikit-learn` (TF-IDF, Naive Bayes, Logistic Regression, Random Forest)
* **OCR & Visión Offline:** `pytesseract`, `OpenCV` (`cv2`)

### Frontend Web (UI)

* Next.js 14+ (App Router, React 18, TypeScript)
* Tailwind CSS (Tema Gótico Obsidian, Crimson y Amethyst)
* Lucide Icons & HTML5 Canvas acelerado por GPU (Rosetones y Partículas)
* Framer Motion & CSS transitions puras (Sidebar colapsable de 256px a 80px)

### Infraestructura

* Docker
* Docker Compose
* Almacenamiento local / Compatible con S3 (MinIO)

---

## 5. Inteligencia del Sistema (Pure Libraries & Local ML)

El sistema **no depende de LLMs externos ni de APIs de inferencia en la nube**.

Toda la inteligencia, clasificación, extracción y normalización se realiza mediante librerías de Python locales y componentes deterministas.

La arquitectura se organiza en capas abstractas e intercambiables:

```text
ExtractionEngine
├── TabularExtractor (CSV / Excel / pandas)
├── PDFTableExtractor (pdfplumber)
├── RuleBasedExtractor (Regex / Patrones)
└── FuzzyEntityExtractor (rapidfuzz / spaCy)

ClassificationEngine
├── RuleClassifier (Keywords / Extensiones / Heurísticas)
└── MLClassifier (scikit-learn pipelines locales)
```

Las reglas de extracción y modelos entrenados deben ejecutarse en local, garantizando privacidad total, latencia mínima y cero coste por llamada.

---

## 6. Documentación

La documentación ubicada en `docs/` representa la fuente de verdad arquitectónica del proyecto.

Cuando una modificación cambia:

* arquitectura;
* API;
* modelo de datos;
* seguridad;
* flujo de procesamiento;
* infraestructura;
* comportamiento importante;

el agente debe actualizar la documentación correspondiente.

No modificar silenciosamente decisiones arquitectónicas documentadas.

Si una decisión anterior parece incorrecta, debe proponerse el cambio antes de aplicarlo cuando el cambio sea significativo.

---

## 7. Desarrollo basado en tareas

No implementar grandes cantidades de código sin planificación.

Para funcionalidades relevantes:

```text
Analizar
↓
Planificar
↓
Implementar
↓
Probar
↓
Revisar
↓
Documentar
```

Antes de modificar código existente, el agente debe comprender primero:

* estructura del proyecto;
* dependencias;
* archivos relacionados;
* tests existentes;
* documentación relevante.

---

## 8. Testing

Toda funcionalidad importante debe tener pruebas apropiadas.

Prioridad:

1. lógica de negocio y parsers de documentos;
2. motores de extracción y clasificadores;
3. validación de esquemas y tipos;
4. autenticación/autorización y aislamiento multi-tenant;
5. endpoints críticos de la API;
6. tareas asíncronas de workers.

No crear tests que únicamente comprueben que una función existe. Los tests deben verificar comportamiento real con fixtures y casos borde (archivos corruptos, formatos inconsistentes, caracteres especiales).

---

## 9. Manejo de errores

Los errores deben ser:

* explícitos;
* controlados;
* registrados cuando sea necesario con contexto suficiente;
* útiles para debugging interno.

No utilizar:

```python
except Exception:
    pass
```

salvo que exista una razón explícita y documentada.

Los errores expuestos a usuarios o clientes API nunca deben contener stack traces ni rutas internas del servidor.

---

## 10. Archivos y documentos

Los archivos proporcionados por usuarios deben considerarse datos no confiables.

Validar:

* tamaño máximo de archivo;
* extensión permitida;
* MIME type real (inspección de cabeceras mágicas);
* estructura del documento (protección contra bombas de descompresión o archivos maliciosos);
* prevención de inyecciones en hojas de cálculo (CSV / Excel Formula Injection: `=cmd|...`).

Los archivos no deben procesarse indefinidamente ni permitir consumo ilimitado de recursos.

---

## 11. Datos sensibles y Privacidad

FlowMind AI trabaja con información empresarial y documental crítica.

Por ello:

* procesamiento 100% local sin filtración a APIs externas;
* minimizar almacenamiento redundante;
* evitar logs con información sensible (PII, tokens, contraseñas);
* aplicar controles de acceso basados en roles (RBAC);
* separar tenants rigurosamente;
* validar permisos en cada capa.

Las decisiones específicas de seguridad se documentarán en:

```text
docs/11-security.md
```

---

## 12. Multi-tenancy

FlowMind AI es una plataforma multi-tenant.

Toda entidad empresarial debe estar asociada a una organización (`organization_id`).

Los datos pertenecientes a una organización nunca deben ser accesibles por otra.

Toda consulta a la base de datos o al almacenamiento debe filtrar explícitamente por el contexto del tenant.

---

## 13. Dependencias

Antes de añadir una dependencia:

1. comprobar si la funcionalidad puede implementarse razonablemente con el stack existente;
2. comprobar mantenimiento, seguridad y compatibilidad;
3. evaluar impacto en peso e inferencia local;
4. justificar su incorporación.

Evitar dependencias innecesarias o paquetes obsoletos.

---

## 14. Variables de entorno

Los secretos y configuraciones específicas del entorno deben utilizar variables de entorno.

Ejemplo:

```text
DATABASE_URL=
REDIS_URL=
SECRET_KEY=
STORAGE_BACKEND=
S3_ENDPOINT=
S3_ACCESS_KEY=
S3_SECRET_KEY=
```

Nunca introducir valores reales o credenciales en el código fuente.

---

## 15. Git

Los commits deben ser pequeños y descriptivos siguiendo Conventional Commits:

```text
feat: add excel extractor for tabular data
fix: sanitize formula injection in csv exports
test: add unit tests for rule based extractor
docs: update architecture document for local processing
refactor: separate classification engine into modular pipelines
```

Evitar commits genéricos como `update`, `changes`, `fix`.

---

## 16. Qué NO debe hacer el agente

No debe:

* reescribir el proyecto completo sin necesidad;
* agregar llamadas o dependencias a LLMs externos (OpenAI, Anthropic, Gemini, etc.);
* cambiar tecnologías sin justificación técnica documentada;
* eliminar tests para solucionar errores;
* eliminar documentación para evitar inconsistencias;
* introducir secretos o datos sensibles;
* generar funcionalidades no solicitadas;
* asumir requisitos que no están definidos;
* crear microservicios innecesarios;
* implementar todo el roadmap de una sola vez.

---

## 17. Prioridad de fuentes

Cuando exista una contradicción:

```text
Requerimiento explícito del usuario
        ↓
Documentación del proyecto (docs/)
        ↓
AGENTS.md
        ↓
GEMINI.md
        ↓
SKILL.md
        ↓
Convenciones generales
```

---

## 18. Estado del proyecto

El proyecto se encuentra en fase inicial.

Foco actual: **MVP de ingesta, parsing local robusto (XLSX, CSV, PDF), extracción determinista de datos estructurados, clasificación clásica y persistencia segura.**

---

## 19. Regla principal

Antes de escribir código, comprender el problema.

Antes de cambiar arquitectura, justificar el cambio.

Antes de agregar una dependencia, evaluar alternativas.

Antes de considerar una funcionalidad terminada, probarla.

Antes de cerrar una tarea importante, actualizar la documentación.
