# FlowMind AI

> **Intelligent Business Process Automation & Enterprise Decision Platform (100% Local & Privacy-First)**

FlowMind AI es una plataforma SaaS B2B y suite de escritorio diseñada para automatizar flujos de trabajo empresariales y toma de decisiones operacionales transformando documentos semi-estructurados y desestructurados (Excel, CSV, PDF, imágenes) en hechos verificados, grafos relacionales y acciones automatizadas con evidencia trazable.

El sistema opera con **cero dependencia de LLMs externos en la nube**, garantizando privacidad absoluta de datos (*Zero Cloud Data Leakage*), tiempos de respuesta en milisegundos y predictibilidad operativa mediante librerías de Machine Learning clásico (`scikit-learn`), NLP local (`rapidfuzz`, `regex`), visión artificial offline (`OpenCV`, `pytesseract`), grafos relacionales (`NetworkX`), validadores matemáticos deterministas y el motor antifraude **FlowMind Sentinel**.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu sistema:

* **Python 3.11+** ([Descargar Python](https://www.python.org/downloads/))
* **Node.js 18+ y npm** ([Descargar Node.js](https://nodejs.org/))
* **Git** ([Descargar Git](https://git-scm.com/))
* *(Opcional)* **Docker & Docker Compose** (solo si deseas usar PostgreSQL, Redis y MinIO en lugar del modo SQLite local por defecto).

---

## 🚀 Guía de Instalación

Puedes instalar todas las dependencias del proyecto de forma **automática (Recomendado)** con un solo script, o siguiendo el flujo **manual paso a paso**.

### 1. Clonar el repositorio

```bash
git clone https://github.com/nastex123/FLOWIA-2.git
cd FLOWIA-2
```

---

### Opción A: Instalación Automática Unificada con `install.py` (Recomendada)

El proyecto incluye el script `install.py` que detecta automáticamente tu sistema operativo, crea el entorno virtual `venv`, instala las dependencias de Python (backend + desktop), inicializa `.env` en modo SQLite local, instala dependencias de frontend (`npm install`) y realiza un *Smoke Test* de verificación:

#### En Windows (PowerShell / CMD):
```powershell
python install.py
# O forzando el modo Windows:
python install.py --os windows
```

#### En Linux / macOS (Bash / Zsh):
```bash
python3 install.py
# O forzando el modo Linux:
python3 install.py --os linux
```

> **Banderas adicionales de `install.py`:**
> * `--backend-only` : Configura únicamente Python (`venv` + backend + desktop) omitiendo `npm`.
> * `--frontend-only` : Ejecuta únicamente `npm install` en el directorio `frontend/`.
> * `--skip-smoke-test` : Omite la verificación final de importaciones.

---

### Opción B: Instalación Manual Paso a Paso

Si prefieres configurar cada paso manualmente:

#### 1. Configurar el Entorno Virtual de Python

**En Windows (PowerShell):**
```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Actualizar pip e instalar dependencias
python -m pip install --upgrade pip
pip install -e ".\backend[dev]"
```

**En Linux / macOS:**
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Actualizar pip e instalar dependencias
pip install --upgrade pip
pip install -e "./backend[dev]"
```

---

### 3. Configurar Variables de Entorno (`.env`)

FlowMind AI funciona **out-of-the-box en modo local** utilizando SQLite asíncrono y almacenamiento en disco local sin requerir servicios externos en ambos sistemas operativos.

Copia la plantilla de variables de entorno según tu sistema:

#### En Windows (PowerShell):
```powershell
Copy-Item .env.example .env
```

#### En Windows (CMD):
```cmd
copy .env.example .env
```

#### En Linux / macOS (Bash / Zsh):
```bash
cp .env.example .env
```

---

## ⚙️ Guía de Variables de Entorno (Windows vs Linux)

Todas las variables se definen en el archivo `.env` en la raíz del proyecto. También puedes exportarlas directamente en tu terminal.

### Tabla de Variables Principales

| Variable | Descripción | Valor Local (Windows) | Valor Local (Linux / macOS) | Modo Docker / Producción |
| :--- | :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Conexión a la base de datos | `sqlite+aiosqlite:///./data/flowmind.db` | `sqlite+aiosqlite:///./data/flowmind.db` | `postgresql+asyncpg://postgres:postgres@localhost:5432/flowmind` |
| `DATABASE_ECHO` | Logging de queries SQL | `false` | `false` | `false` |
| `REDIS_URL` | Cola de tareas y caché Redis | *(Comentado o vacío)* | *(Comentado o vacío)* | `redis://localhost:6379/0` |
| `STORAGE_BACKEND` | Motor de almacenamiento | `local` | `local` | `local` o `s3` |
| `LOCAL_STORAGE_PATH` | Ruta de archivos subidos | `./data/storage` o `C:/flowmind/data` | `./data/storage` o `/var/flowmind/data` | `./data/storage` |
| `SECRET_KEY` | Llave secreta para tokens JWT | `tu-clave-secreta-min-32-caracteres` | `tu-clave-secreta-min-32-caracteres` | *(Cadena aleatoria segura)* |
| `ALLOWED_ORIGINS` | Orígenes CORS permitidos | `["http://localhost:3000"]` | `["http://localhost:3000"]` | `["https://app.tuempresa.com"]` |
| `MAX_UPLOAD_SIZE_MB` | Tamaño máx. de archivo subido | `25` | `25` | `50` |
| `ALLOWED_EXTENSIONS` | Extensiones permitidas | `["xlsx","xls","csv","pdf","png","jpg"]` | `["xlsx","xls","csv","pdf","png","jpg"]` | `["xlsx","xls","csv","pdf","png","jpg"]` |
| `S3_ENDPOINT` *(solo S3)* | Endpoint de MinIO / AWS S3 | `http://localhost:9000` | `http://localhost:9000` | `http://minio:9000` |
| `S3_ACCESS_KEY` *(solo S3)* | Clave de acceso S3 | `minioadmin` | `minioadmin` | *(Credencial segura)* |
| `S3_SECRET_KEY` *(solo S3)* | Clave secreta S3 | `minioadmin` | `minioadmin` | *(Credencial segura)* |
| `S3_BUCKET_NAME` *(solo S3)* | Nombre del bucket S3 | `flowmind-documents` | `flowmind-documents` | `flowmind-documents` |

### Cómo Definir Variables en Terminal (Overrides Temporales)

Si necesitas sobreescribir una variable temporalmente sin modificar `.env`:

#### En Windows (PowerShell):
```powershell
$env:DATABASE_URL = "sqlite+aiosqlite:///./data/flowmind.db"
$env:STORAGE_BACKEND = "local"
$env:LOCAL_STORAGE_PATH = "./data/storage"
$env:FLOWMIND_API_URL = "http://127.0.0.1:8000"
```

#### En Windows (CMD):
```cmd
set DATABASE_URL=sqlite+aiosqlite:///./data/flowmind.db
set STORAGE_BACKEND=local
set LOCAL_STORAGE_PATH=./data/storage
set FLOWMIND_API_URL=http://127.0.0.1:8000
```

#### En Linux / macOS (Bash / Zsh):
```bash
export DATABASE_URL="sqlite+aiosqlite:///./data/flowmind.db"
export STORAGE_BACKEND="local"
export LOCAL_STORAGE_PATH="./data/storage"
export FLOWMIND_API_URL="http://127.0.0.1:8000"
```

> 📌 **Consejo sobre rutas en Windows:**  
> En los archivos `.env` y variables de entorno, se recomienda usar barras inclinadas normales (`/`) o rutas relativas como `./data/storage`. Python normaliza automáticamente las rutas en Windows y Linux.


---

### 4. Instalar Dependencias del Frontend (Web Dashboard)

```bash
cd frontend
npm install
cd ..
```

*(Nota: Si omites este paso, el script lanzador `start.py` detectará automáticamente si falta `node_modules` y ejecutará `npm install` por ti si usas la bandera `--web`).*

---

## ⚡ Cómo Iniciar la Aplicación

### Opción 1: Lanzador Unificado (Recomendado)

Inicia automáticamente el Backend (FastAPI con autodetección de puertos libres) y la Suite de Escritorio PySide6 con un solo comando:

#### En Windows (PowerShell):
```powershell
# Asegúrate de tener el entorno virtual activo: .\venv\Scripts\Activate.ps1
.\start.ps1

# O directamente con python:
python start.py
```

#### En Linux o macOS:
```bash
# Asegúrate de tener el entorno virtual activo: source venv/bin/activate
chmod +x start.sh
./start.sh

# O directamente con python:
python3 start.py
```

#### Banderas adicionales para `start.py`:
* `python start.py --web` : Inicia Backend + Desktop UI + Frontend Web (Next.js en `http://localhost:3000`).
* `python start.py --no-ui` : Inicia únicamente el Backend FastAPI sin abrir la interfaz de escritorio.

---

### Opción 2: Iniciar Servicios de Forma Individual (Terminales Separadas)

Si prefieres ejecutar cada componente por separado en desarrollo:

#### Terminal 1 — Backend API (FastAPI)
```bash
# Con el entorno virtual activo:
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
* **API disponible en:** `http://127.0.0.1:8000`
* **Swagger Docs:** `http://127.0.0.1:8000/docs`

#### Terminal 2 — Suite de Escritorio Nativa (PySide6 / Qt6)
```bash
# Con el entorno virtual activo:
python desktop/main.py
```
* Permite procesar documentos sin conexión, inspeccionar anomalías, validar facturas y monitorear carpetas *Hot-Folder* en segundo plano.

#### Terminal 3 — Frontend Web (Next.js)
```bash
cd frontend
npm run dev
```
* **Dashboard Web disponible en:** `http://localhost:3000`

---

### Opción 3: Infraestructura Empresarial con Docker (PostgreSQL + Redis + MinIO)

Si deseas utilizar la infraestructura completa en lugar del modo SQLite local:

```bash
docker compose -f infrastructure/docker-compose.yml up -d
```

Esto levantará los siguientes servicios:
* **PostgreSQL:** `localhost:5432` (db: `flowmind`, user: `postgres`, pass: `postgres`)
* **Redis:** `localhost:6379`
* **MinIO S3:** `http://localhost:9000` (Consola: `http://localhost:9001`, credenciales: `minioadmin` / `minioadmin`)

---

## 🔑 Credenciales y Acceso por Defecto

Al iniciar el backend por primera vez en modo local, se inicializa automáticamente la base de datos con un usuario administrador predeterminado:

| Parámetro | Valor por Defecto |
| :--- | :--- |
| **URL Frontend Web** | `http://localhost:3000` |
| **Documentación API (Swagger)** | `http://127.0.0.1:8000/docs` |
| **Usuario / Email** | `admin@flowmind.local` |
| **Contraseña** | `admin123` |
| **Organización** | `default-org` |

> 🔒 *Puedes interactuar vía API mediante `Authorization: Bearer <token>` o generando una API Key (`fm_...`) desde la sección de configuración.*

---

## 📄 Generar Documentos de Muestra para Pruebas

Para generar un conjunto de documentos empresariales realistas (Facturas XLSX, Inventarios CSV, Pedidos y PDFs con tablas):

```bash
python scripts/generate_sample_documents.py
```

Los archivos de muestra se generarán en la carpeta `samples/` listos para ser procesados desde la web o la suite de escritorio.

---

## 🧪 Ejecutar Pruebas Automatizadas

```bash
# Con el entorno virtual activo:
pytest tests/
```

---

## 🏛️ Estructura del Proyecto

```text
FLOWIA-2/
├── AGENTS.md                  # Reglas de desarrollo para agentes IA
├── GEMINI.md                  # Contexto operativo para el agente
├── install.py                 # Instalador automatizado multiplataforma (Windows / Linux)
├── start.py                   # Lanzador unificado multiplataforma (Backend + Desktop + Web)
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
│   ├── ui/                    # MainWindow (Dark Theme, Grid Pro, Inspector, Review)
│   └── main.py                # Punto de entrada de la aplicación de escritorio
├── frontend/                  # Interfaz web en Next.js 14 + React + Tailwind CSS
├── infrastructure/            # Definiciones Docker Compose (PostgreSQL, Redis, MinIO)
├── samples/                   # Documentos reales de prueba (XLSX, CSV, PDF)
├── scripts/                   # Scripts auxiliares y generador de archivos de muestra
├── tests/                     # Suite completa de pruebas unitarias e integración
└── docs/                      # Fuente de verdad arquitectónica y técnica
```

---

## 📜 Índice de Documentación Técnica

Para profundizar en el diseño y arquitectura del sistema, consulta la documentación en `docs/`:

* **00 — Visión:** [`docs/00-vision/01-vision.md`](docs/00-vision/01-vision.md) — Filosofía de privacidad *Zero Cloud Data Leakage*.
* **01 — Producto:**
  * [`docs/01-product/01-prd.md`](docs/01-product/01-prd.md) — Requisitos del producto (FRs, NFRs y Personas).
  * [`docs/01-product/02-schemas-and-mapping.md`](docs/01-product/02-schemas-and-mapping.md) — Esquemas canónicos y normalización difusa.
  * [`docs/01-product/03-roadmap.md`](docs/01-product/03-roadmap.md) — Fases de entrega y roadmap.
* **03 — Arquitectura:**
  * [`docs/03-architecture/01-general-architecture.md`](docs/03-architecture/01-general-architecture.md) — Arquitectura general (*Document Plane & Decision Plane*).
  * [`docs/03-architecture/02-enterprise-decision-engine.md`](docs/03-architecture/02-enterprise-decision-engine.md) — Grafo de Hechos (NetworkX), Validador Matemático y Sentinel.
  * [`docs/03-architecture/03-desktop-pyside6.md`](docs/03-architecture/03-desktop-pyside6.md) — Suite de escritorio nativa PySide6.
* **04 — Ingeniería & APIs:**
  * [`docs/04-engineering/01-api-reference.md`](docs/04-engineering/01-api-reference.md) — Referencia de endpoints REST.
  * [`docs/04-engineering/02-database.md`](docs/04-engineering/02-database.md) — Base de datos asíncrona y migraciones.
  * [`docs/04-engineering/03-advanced-engines.md`](docs/04-engineering/03-advanced-engines.md) — Conciliación a 3 vías, Norma 43, Barcode/QR, OMR y Nóminas.
* **05 — Inteligencia Artificial Local:** [`docs/05-ai/01-local-ai-architecture.md`](docs/05-ai/01-local-ai-architecture.md) — Machine Learning local y TF-IDF sin LLMs externos.
* **06 — Seguridad & Cumplimiento:** [`docs/06-security/01-security-and-privacy.md`](docs/06-security/01-security-and-privacy.md) — Seguridad, RBAC y aislamiento multi-tenant.