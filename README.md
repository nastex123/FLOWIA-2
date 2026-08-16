# FlowMind AI

> **Intelligent Business Process Automation Platform (100% Local & Privacy-First)**

FlowMind AI es una plataforma SaaS B2B diseñada para automatizar flujos de trabajo empresariales transformando documentos semi-estructurados y desestructurados (Excel, CSV, PDF) en datos estructurados, normalizados y accionables.

El sistema opera con **cero dependencia de LLMs externos en la nube**, garantizando **privacidad absoluta de datos (Zero Cloud Data Leakage)**, tiempos de respuesta en milisegundos y predictibilidad operativa mediante librerías de Machine Learning clásico (`scikit-learn`), NLP local (`rapidfuzz`, `regex`) y motores deterministas de extracción.

---

## 🏛️ Arquitectura del Repositorio

```text
FlowMind-AI-Repository-Development/
├── AGENTS.md                  # Reglas maestras de desarrollo para agentes IA
├── GEMINI.md                  # Contexto operativo para el agente
├── skills/                    # Metodologías especializadas de desarrollo
├── docs/                      # Fuente de verdad arquitectónica
│   ├── 01-architecture.md     # Diseño del sistema y módulos
│   ├── 02-mvp-roadmap.md      # Fases de desarrollo del MVP
│   ├── 03-schemas-and-mapping.md # Motor de esquemas y mapeo difuso
│   ├── 04-api-reference.md    # Referencia completa de la API REST
│   └── 11-security.md         # Modelo de seguridad y aislamiento multi-tenant
├── backend/                   # API REST en FastAPI + Pydantic v2 + SQLite/SQLAlchemy
│   ├── app/
│   │   ├── core/              # Configuración y utilidades core
│   │   ├── domain/            # Schemas Pydantic y DTOs
│   │   ├── infrastructure/    # Persistencia DB (SQLite/PostgreSQL) y Presets
│   │   └── services/          # Parsers, Extractores locales, Clasificadores ML y Mapeo
├── frontend/                  # Interfaz web en Next.js 14 + TypeScript + Tailwind CSS
├── samples/                   # Documentos reales de prueba (XLSX, CSV, PDF)
├── scripts/                   # Scripts de inicio y generador de archivos
└── tests/                     # Suite de pruebas unitarias e integración (36 tests)
```

---

## 🚀 Pila Tecnológica

* **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy (Asyncio), SQLite (`aiosqlite`) / PostgreSQL.
* **Inteligencia Local (Pure Libraries & Local ML):**
  * *Tabular:* `pandas`, `openpyxl`, `csv`
  * *Documentos & PDF:* `PyMuPDF` (`pymupdf`), `pdfplumber`
  * *Extracción & Matching:* `rapidfuzz`, `regex`
  * *Clasificación ML:* `scikit-learn` (TF-IDF, LogisticRegression)
* **Frontend:** Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Lucide Icons.

---

## 🛠️ Inicio Rápido en Local (Windows)

### 1. Iniciar el Backend (Terminal 1)
```powershell
.\scripts\start_backend.ps1
```
* **API REST:** `http://127.0.0.1:8000`
* **Swagger UI interactivo:** `http://127.0.0.1:8000/docs`

### 2. Iniciar el Frontend (Terminal 2)
```powershell
.\scripts\start_frontend.ps1
```
* **Aplicación Web:** `http://localhost:3000`
* **Gestor de Esquemas:** `http://localhost:3000/schemas`
* **Automatización & Seguridad:** `http://localhost:3000/settings`

### 3. Acceder a la Plataforma
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
Los archivos se guardarán automáticamente en `samples/` listos para ser arrastrados a la interfaz web.

---

## 🧪 Ejecutar Pruebas Automatizadas

```powershell
# Ejecutar la suite completa de 36 tests
python -m pytest tests/
```

---

## 📜 Reglas de Contribución y Documentación

* [`AGENTS.md`](file:///C:/Users/Usuario/Documents/GitHub/FlowMind-AI-Repository-Development/AGENTS.md)
* [`docs/01-architecture.md`](file:///C:/Users/Usuario/Documents/GitHub/FlowMind-AI-Repository-Development/docs/01-architecture.md)
* [`docs/03-schemas-and-mapping.md`](file:///C:/Users/Usuario/Documents/GitHub/FlowMind-AI-Repository-Development/docs/03-schemas-and-mapping.md)
* [`docs/04-api-reference.md`](file:///C:/Users/Usuario/Documents/GitHub/FlowMind-AI-Repository-Development/docs/04-api-reference.md)
* [`docs/11-security.md`](file:///C:/Users/Usuario/Documents/GitHub/FlowMind-AI-Repository-Development/docs/11-security.md)
