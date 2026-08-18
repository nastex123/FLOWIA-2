# FlowMind AI

> **Intelligent Business Process Automation & Enterprise Decision Platform (100% Local & Privacy-First)**

FlowMind AI es una plataforma SaaS B2B y suite de escritorio diseñada para automatizar flujos de trabajo empresariales y toma de decisiones operacionales transformando documentos semi-estructurados y desestructurados (Excel, CSV, PDF, imágenes) en **hechos verificados, grafos relacionales y acciones automatizadas con evidencia trazable**.

El sistema opera con **cero dependencia de LLMs externos en la nube**, garantizando **privacidad absoluta de datos (Zero Cloud Data Leakage)**, tiempos de respuesta en milisegundos y predictibilidad operativa mediante librerías de Machine Learning clásico (`scikit-learn`), NLP local (`rapidfuzz`, `regex`), visión artificial offline (`OpenCV`, `zxing-cpp`, `pyzbar`, `pytesseract`), grafos relacionales (`NetworkX`), validadores matemáticos deterministas y el motor antifraude `FlowMind Sentinel`.

---

## 🏛️ Arquitectura del Repositorio

```text
FlowMind-AI-Repository-Development/
├── AGENTS.md                  # Reglas maestras de desarrollo para agentes IA
├── GEMINI.md                  # Contexto operativo para el agente
├── skills/                    # Metodologías especializadas de desarrollo
├── docs/                      # Fuente de verdad arquitectónica
│   ├── 01-architecture.md     # Diseño global del sistema (Document Plane & Decision Plane)
│   ├── 02-mvp-roadmap.md      # Fases de entrega y roadmap de expansión (Fases 1 a 12)
│   ├── 03-schemas-and-mapping.md # Motor de esquemas canónicos y mapeo difuso
│   ├── 04-api-reference.md    # Referencia completa de la API REST
│   ├── 05-desktop-pyside6.md  # Suite de escritorio nativa PySide6 y Tray Agent
│   ├── 06-advanced-engines.md # Conciliación 3 vías, Norma 43, Barcode/QR, OMR y Nóminas
│   ├── 07-local-search-and-compliance.md # Búsqueda vectorial FAISS, SII AEAT y Verifactu
│   ├── 08-enterprise-decision-engine.md  # Fact Graph, Validador Matemático y FlowMind Sentinel
│   └── 11-security.md         # Modelo de seguridad, RBAC y aislamiento multi-tenant
├── backend/                   # API REST en FastAPI + Pydantic v2 + SQLite/SQLAlchemy
│   ├── app/
│   │   ├── api/routers/       # Endpoints REST (/documents, /schemas, /automation, /decision, /business, /compliance, /auth)
│   │   ├── core/              # Configuración, excepciones y seguridad
│   │   ├── domain/            # Modelos de dominio Pydantic y DTOs
│   │   ├── infrastructure/    # Persistencia DB (SQLite/PostgreSQL) y Presets
│   │   └── services/          # Extractores, Clasificadores, Decision, Business, Compliance & Sentinel
├── desktop/                   # Suite de escritorio nativa en PySide6 (Qt6)
│   ├── controllers/           # Cliente local / API
│   ├── models/                # VirtualDataTableModel (QAbstractTableModel)
│   ├── services/              # HotFolderWatcher con watchdog
│   ├── ui/                    # MainWindow (Dark Theme, Grid Pro, Inspector)
│   └── main.py                # Lanzador de la app de escritorio
├── frontend/                  # Interfaz web en Next.js 14 + TypeScript + Tailwind CSS
├── samples/                   # Documentos reales de prueba (XLSX, CSV, PDF)
├── scripts/                   # Scripts de utilidades y generador de archivos de muestra
├── start.py                   # Lanzador unificado multiplataforma (Windows / Linux / macOS)
├── start.sh                   # Script ejecutable bash para Linux / macOS
├── start.ps1                  # Script PowerShell para Windows
└── tests/                     # Suite de pruebas unitarias e integración (73 tests)
```

---

## 🚀 Pila Tecnológica

* **Backend & API:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy (Asyncio), SQLite (`aiosqlite`) / PostgreSQL.
* **Escritorio Nativo:** PySide6 (Qt6), `watchdog` (Hot-Folder Tray Agent), `VirtualDataTableModel`.
* **Inteligencia Local, Grafos & Compliance (Pure Libraries & Local ML):**
  * *Tabular & Hojas de Cálculo:* `pandas`, `openpyxl`, `csv`, `numpy`
  * *Documentos & PDF:* `PyMuPDF` (`fitz`), `pdfplumber`
  * *Visión Artificial & OCR:* `OpenCV`, `zxing-cpp`, `pyzbar`, `pytesseract`
  * *Extracción & Normalización Difusa:* `rapidfuzz`, `regex`
  * *Grafos Relacionales de Hechos:* `NetworkX`
  * *Clasificación ML & Embeddings:* `scikit-learn` (TF-IDF, LogisticRegression, IsolationForest)
  * *Motores de Negocio:* Conciliación a 3 Vías, Parser Bancario Norma 43 / CSB 43, Desagregador de Nóminas
  * *Cumplimiento Fiscal & Privacidad:* Generador XML AEAT SII, Hash Chaining Veri*factu (RD 1007/2023), Redactor PII/GDPR
* **Frontend Web:** Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Lucide Icons.

---

## 🛠️ Inicio Rápido Unificado (Comando Único)

Puedes iniciar **Backend y Frontend simultáneamente** con un único comando multiplataforma:

### En Windows:
```powershell
# Opción 1 (Python multiplataforma):
python start.py

# Opción 2 (PowerShell directo):
.\start.ps1
```

### En Linux o macOS:
```bash
# Opción 1 (Bash script ejecutable):
chmod +x start.sh
./start.sh

# Opción 2 (Python directo):
python3 start.py
```

* **Backend API (FastAPI):** `http://127.0.0.1:8000`
* **Swagger Docs interactivo:** `http://127.0.0.1:8000/docs`
* **Web Dashboard (Next.js):** `http://localhost:3000`
* **Gestor de Esquemas:** `http://localhost:3000/schemas`
* **Automatización & Seguridad:** `http://localhost:3000/settings`

### Iniciar la Suite de Escritorio Nativa (PySide6)
```powershell
python desktop/main.py
```
Permite procesar documentos sin conexión a red, visualizar tablas masivas con aceleración y monitorizar carpetas *Hot-Folder* en segundo plano.

### Acceder a la Plataforma
Al iniciarse, el backend crea automáticamente una organización y un usuario administrador por defecto:

* **Correo:** `admin@flowmind.local`
* **Contraseña:** `admin123`
* **Organización:** `default-org`

Inicia sesión en `http://localhost:3000/login`. Todo el frontend exige autenticación; también puedes integrar vía API con `Authorization: Bearer <jwt>` o una API Key (`fm_...`) creada desde `/settings`.

---

## 📄 Generar Documentos de Prueba

Para generar o regenerar documentos de negocio realistas (Facturas Excel, Inventarios CSV, Pedidos y PDFs):

```powershell
python scripts/generate_sample_documents.py
```
Los archivos se guardarán automáticamente en `samples/` listos para ser arrastrados a la interfaz web o al cliente de escritorio.

---

## 🧪 Ejecutar Pruebas Automatizadas

```powershell
# Ejecutar la suite completa de 73 tests
python -m pytest tests/
```

---

## 📜 Documentación Técnica Completa

La documentación del proyecto se organiza conforme al estándar de `documentation` skill:

* **00 — Visión:** [`docs/00-vision/01-vision.md`](docs/00-vision/01-vision.md) — Filosofía de privacidad Zero Cloud Data Leakage y público objetivo.
* **01 — Producto:**
  * [`docs/01-product/01-prd.md`](docs/01-product/01-prd.md) — Product Requirements Document (FRs, NFRs y Personas).
  * [`docs/01-product/02-schemas-and-mapping.md`](docs/01-product/02-schemas-and-mapping.md) — Esquemas canónicos y normalización con RapidFuzz.
  * [`docs/01-product/03-roadmap.md`](docs/01-product/03-roadmap.md) — Fases de entrega y estado de avance de componentes.
* **03 — Arquitectura:**
  * [`docs/03-architecture/01-general-architecture.md`](docs/03-architecture/01-general-architecture.md) — Diseño global del sistema (Document Plane & Decision Plane).
  * [`docs/03-architecture/02-enterprise-decision-engine.md`](docs/03-architecture/02-enterprise-decision-engine.md) — Grafo de Hechos (`NetworkX`), Validador Matemático y FlowMind Sentinel.
  * [`docs/03-architecture/03-desktop-pyside6.md`](docs/03-architecture/03-desktop-pyside6.md) — Suite de escritorio nativa PySide6 y Tray Agent.
* **04 — Ingeniería & APIs:**
  * [`docs/04-engineering/01-api-reference.md`](docs/04-engineering/01-api-reference.md) — Referencia exhaustiva de endpoints REST.
  * [`docs/04-engineering/02-database.md`](docs/04-engineering/02-database.md) — Base de datos asíncrona y migraciones con Alembic.
  * [`docs/04-engineering/03-advanced-engines.md`](docs/04-engineering/03-advanced-engines.md) — Conciliación 3 vías, Norma 43, Barcode/QR, OMR y Nóminas.
* **05 — Inteligencia Artificial Local:** [`docs/05-ai/01-local-ai-architecture.md`](docs/05-ai/01-local-ai-architecture.md) — Pipeline de ML clásico, TF-IDF y ausencia de LLMs externos.
* **06 — Seguridad & Cumplimiento:**
  * [`docs/06-security/01-security-and-privacy.md`](docs/06-security/01-security-and-privacy.md) — Directrices de seguridad, RBAC y aislamiento multi-tenant.
  * [`docs/06-security/02-compliance-and-pii.md`](docs/06-security/02-compliance-and-pii.md) — Cumplimiento fiscal AEAT SII, Veri\*factu y redactor PII/RGPD.
* **08 — Operaciones & Roadmap:** [`docs/08-operations/01-expansion-proposals.md`](docs/08-operations/01-expansion-proposals.md) — 22 Propuestas estratégicas de expansión futura.
* **09 — Decisiones Arquitectónicas (ADRs):**
  * [`docs/09-decisions/ADR-001-local-deterministic-engine.md`](docs/09-decisions/ADR-001-local-deterministic-engine.md) — Inferencia 100% local sin LLMs en la nube.
  * [`docs/09-decisions/ADR-002-two-plane-architecture.md`](docs/09-decisions/ADR-002-two-plane-architecture.md) — Desacoplamiento de Document Plane y Decision Plane.


