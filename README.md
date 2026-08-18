FlowMind AI
Intelligent Business Process Automation & Enterprise Decision Platform (100% Local & Privacy-First)

FlowMind AI es una plataforma SaaS B2B y suite de escritorio diseñada para automatizar flujos de trabajo empresariales y toma de decisiones operacionales transformando documentos semi-estructurados y desestructurados (Excel, CSV, PDF, imágenes) en hechos verificados, grafos relacionales y acciones automatizadas con evidencia trazable.

El sistema opera con cero dependencia de LLMs externos en la nube, garantizando privacidad absoluta de datos (Zero Cloud Data Leakage), tiempos de respuesta en milisegundos y predictibilidad operativa mediante librerías de Machine Learning clásico (scikit-learn), NLP local (rapidfuzz, regex), visión artificial offline (OpenCV, zxing-cpp, pyzbar, pytesseract), grafos relacionales (NetworkX), validadores matemáticos deterministas y el motor antifraude FlowMind Sentinel.

📋 Requisitos Previos
Antes de comenzar, asegúrate de tener instalado en tu sistema:

Python 3.11+ (Descargar Python)
Node.js 18+ y npm (Descargar Node.js)
Git (Descargar Git)
(Opcional) Docker & Docker Compose (solo si deseas usar PostgreSQL, Redis y MinIO en lugar del modo SQLite local por defecto).
🚀 Guía de Instalación Rápida (Paso a Paso)
Sigue estos pasos para clonar el repositorio, configurar el entorno e iniciar el proyecto desde cero:

1. Clonar el repositorio
git clone <URL_DEL_REPOSITORIO>
cd FLOWIA-2
2. Configurar el entorno virtual de Python
En Linux / macOS:
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Actualizar pip e instalar dependencias del backend y suite de escritorio
pip install --upgrade pip
pip install -e "./backend[dev]"
En Windows (PowerShell):
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Actualizar pip e instalar dependencias del backend y suite de escritorio
pip install --upgrade pip
pip install -e ".\backend[dev]"
3. Variables de Entorno (Opcional para modo local)
FlowMind AI funciona out-of-the-box en modo local utilizando SQLite asíncrono y almacenamiento en disco local sin requerir configuración extra.

Si deseas personalizar variables o conectar servicios externos (PostgreSQL, Redis, MinIO), copia la plantilla:

# Linux / macOS
cp .env.example .env

# Windows PowerShell
Copy-Item .env.example .env
4. Instalar dependencias del Frontend (Web Dashboard)
cd frontend
npm install
cd ..
(Nota: Si omites este paso, el script lanzador start.py detectará automáticamente que falta node_modules y ejecutará npm install por ti).

⚡ Cómo Iniciar la Aplicación
Opción 1: Lanzador Unificado (Recomendado)
Inicia Backend (FastAPI) y Frontend (Next.js) simultáneamente con un solo comando:

En Linux o macOS:
# Asegúrate de tener el entorno virtual activo: source venv/bin/activate
chmod +x start.sh
./start.sh

# O directamente con python:
python3 start.py
En Windows (PowerShell):
# Asegúrate de tener el entorno virtual activo: .\venv\Scripts\Activate.ps1
.\start.ps1

# O directamente con python:
python start.py
Opción 2: Iniciar Servicios de Forma Individual (Terminales Separadas)
Si prefieres ejecutar cada componente por separado en desarrollo:

Terminal 1 — Backend API (FastAPI)
# Activa el entorno virtual primero
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
API disponible en: http://127.0.0.1:8000
Documentación interactiva Swagger: http://127.0.0.1:8000/docs
Terminal 2 — Frontend Web (Next.js)
cd frontend
npm run dev
Dashboard Web disponible en: http://localhost:3000
Terminal 3 — Suite de Escritorio Nativa (PySide6 / Qt6 - Opcional)
# Con el entorno virtual activo:
python desktop/main.py
Permite procesar documentos sin conexión, monitorear carpetas Hot-Folder en segundo plano y visualización de datos de alta velocidad.
Opción 3: Infraestructura con Docker (PostgreSQL + Redis + MinIO)
Si deseas utilizar la infraestructura completa de grado empresarial en lugar de SQLite:

docker compose -f infrastructure/docker-compose.yml up -d
Esto levantará:

PostgreSQL: localhost:5432 (db: flowmind, user: postgres, pass: postgres)
Redis: localhost:6379
MinIO S3: http://localhost:9000 (Consola: http://localhost:9001, credenciales: minioadmin/minioadmin)
🔑 Credenciales y Acceso por Defecto
Al iniciar el sistema por primera vez, el backend inicializa automáticamente la base de datos con un usuario administrador:

Parámetro	Valor por Defecto
URL Web	http://localhost:3000
Documentación API	http://127.0.0.1:8000/docs
Usuario / Email	admin@flowmind.local
Contraseña	admin123
Organización	default-org
Inicia sesión en http://localhost:3000/login. Todo el frontend exige autenticación; también puedes interactuar vía API mediante Authorization: Bearer <token> o generando una API Key (fm_...) desde /settings.

📄 Generar Documentos de Prueba
Para generar un conjunto de documentos empresariales realistas (Facturas XLSX, Inventarios CSV, Pedidos y PDFs con tablas):

python scripts/generate_sample_documents.py
Los archivos de muestra se generarán en la carpeta samples/ listos para ser procesados desde la web o la app de escritorio.

🧪 Ejecutar Pruebas Automatizadas
# Con el entorno virtual activo:
python -m pytest tests/
🏛️ Estructura del Proyecto
FLOWIA-2/
├── AGENTS.md                  # Reglas de desarrollo para agentes IA
├── GEMINI.md                  # Contexto operativo para el agente
├── start.py                   # Lanzador unificado multiplataforma (Backend + Frontend)
├── start.sh                   # Script de inicio para Linux / macOS
├── start.ps1                  # Script de inicio para Windows PowerShell
├── .env.example               # Plantilla de variables de entorno
├── backend/                   # API REST en FastAPI + Pydantic v2 + SQLite/SQLAlchemy
│   ├── app/
│   │   ├── api/routers/       # Endpoints REST (/documents, /schemas, /automation, /decision, /auth)
│   │   ├── core/              # Configuración, excepciones y seguridad
│   │   ├── domain/            # Modelos de dominio Pydantic y DTOs
│   │   ├── infrastructure/    # Persistencia DB y Presets
│   │   └── services/          # Extractores, Clasificadores, Decision, Business & Sentinel
│   └── pyproject.toml         # Dependencias y configuración de empaquetado backend
├── desktop/                   # Suite de escritorio nativa en PySide6 (Qt6)
│   ├── controllers/           # Cliente local / API
│   ├── models/                # VirtualDataTableModel
│   ├── services/              # HotFolderWatcher con watchdog
│   ├── ui/                    # MainWindow (Dark Theme, Grid Pro, Inspector)
│   └── main.py                # Punto de entrada de la aplicación de escritorio
├── frontend/                  # Interfaz web en Next.js 14 + React + Tailwind CSS
├── infrastructure/            # Definiciones Docker Compose (PostgreSQL, Redis, MinIO)
├── samples/                   # Documentos reales de prueba (XLSX, CSV, PDF)
├── scripts/                   # Scripts auxiliares y generador de archivos de muestra
├── tests/                     # Suite completa de pruebas unitarias e integración
└── docs/                      # Fuente de verdad arquitectónica y técnica
📜 Documentación Técnica
Para profundizar en el diseño y arquitectura del sistema, consulta la documentación en docs/:

00 — Visión: docs/00-vision/01-vision.md — Filosofía de privacidad Zero Cloud Data Leakage.
01 — Producto:
docs/01-product/01-prd.md — Requisitos del producto (FRs, NFRs y Personas).
docs/01-product/02-schemas-and-mapping.md — Esquemas canónicos y normalización difusa.
docs/01-product/03-roadmap.md — Fases de entrega y roadmap.
03 — Arquitectura:
docs/03-architecture/01-general-architecture.md — Arquitectura general (Document Plane & Decision Plane).
docs/03-architecture/02-enterprise-decision-engine.md — Grafo de Hechos (NetworkX), Validador Matemático y Sentinel.
docs/03-architecture/03-desktop-pyside6.md — Suite de escritorio nativa PySide6.
04 — Ingeniería & APIs:
docs/04-engineering/01-api-reference.md — Referencia de endpoints REST.
docs/04-engineering/02-database.md — Base de datos asíncrona y migraciones.
docs/04-engineering/03-advanced-engines.md — Conciliación a 3 vías, Norma 43, Barcode/QR, OMR y Nóminas.
05 — Inteligencia Artificial Local: docs/05-ai/01-local-ai-architecture.md — Machine Learning local y TF-IDF sin LLMs externos.
06 — Seguridad & Cumplimiento: docs/06-security/01-security-and-privacy.md — Seguridad, RBAC y aislamiento multi-tenant.