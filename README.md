# FlowMind AI

> **Intelligent Business Process Automation Platform (100% Local & Privacy-First)**

FlowMind AI es una plataforma SaaS B2B diseñada para automatizar flujos de trabajo empresariales transformando documentos semi-estructurados y desestructurados (Excel, CSV, PDF, formularios) en datos estructurados y acciones automatizadas.

El sistema opera con **cero dependencia de LLMs externos en la nube**, garantizando privacidad absoluta de datos (Zero Data Leakage), tiempos de respuesta en milisegundos y predictibilidad operativa mediante librerías de Machine Learning clásico, NLP local y motores deterministas de extracción.

---

## 🏛️ Arquitectura del Repositorio

```text
FlowMind-AI-Repository-Development/
├── AGENTS.md                  # Reglas maestras de desarrollo para agentes IA
├── GEMINI.md                  # Contexto operativo para el agente
├── skills/                    # Metodologías especializadas de desarrollo
│   └── flowmind-development/
├── docs/                      # Fuente de verdad arquitectónica
│   ├── 01-architecture.md     # Diseño del sistema y módulos
│   ├── 02-mvp-roadmap.md      # Fases de desarrollo del MVP
│   └── 11-security.md         # Modelo de seguridad y aislamiento multi-tenant
├── backend/                   # API REST en FastAPI + Pydantic v2 + SQLAlchemy
│   ├── app/
│   │   ├── api/               # Endpoints REST y autenticación
│   │   ├── core/              # Configuración y utilidades core
│   │   ├── domain/            # Schemas Pydantic y modelos de dominio
│   │   ├── infrastructure/    # Persistencia y conexiones DB / Storage
│   │   └── services/          # Parsers, Extractores locales y Clasificadores ML
├── workers/                   # Procesamiento asíncrono en background
├── frontend/                  # Interfaz web en Next.js + React + Tailwind
├── infrastructure/            # Docker Compose para PostgreSQL + Redis + MinIO
└── tests/                     # Suite de pruebas unitarias e integración
```

---

## 🚀 Pila Tecnológica

* **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy (Asyncio), Alembic.
* **Inteligencia Local (Pure Libraries):**
  * *Tabular:* `pandas`, `openpyxl`, `csv`
  * *Documentos & PDF:* `PyMuPDF` (`fitz`), `pdfplumber`
  * *Extracción & Matching:* `rapidfuzz`, `regex`, `spacy`
  * *Clasificación ML:* `scikit-learn` (TF-IDF, MultinomialNB, LogisticRegression)
* **Base de Datos & Colas:** PostgreSQL, Redis.
* **Almacenamiento:** Compatible con S3 (MinIO) o sistema de archivos local.
* **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS.

---

## 🛠️ Inicio Rápido (Desarrollo Local)

### 1. Variables de Entorno
Copia la plantilla de entorno:
```bash
cp .env.example .env
```

### 2. Levantar Infraestructura Base
```bash
docker compose -f infrastructure/docker-compose.yml up -d
```

### 3. Backend Setup & Tests
```bash
cd backend
pip install -e .
pytest ../tests
```

---

## 📜 Reglas de Contribución y Desarrollo

Antes de realizar cualquier modificación al código, consulta:
* [`AGENTS.md`](file:///AGENTS.md)
* [`docs/01-architecture.md`](file:///docs/01-architecture.md)
* [`docs/11-security.md`](file:///docs/11-security.md)
