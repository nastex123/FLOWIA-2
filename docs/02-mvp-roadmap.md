# 02 — Roadmap de Desarrollo de FlowMind AI

Este documento define el estado de avance y las fases de entrega de **FlowMind AI**.

---

## Objetivo del Sistema

Construir una plataforma de **Inteligencia Operacional y Automatización Empresarial** autónoma, determinista y privada que transforme documentos de negocio en hechos verificados, relaciones relacionales (Grafo de Hechos), validaciones matemáticas estrictas y detección antifraude sin dependencias en la nube.

---

## Estado de las Fases de Implementación

### ✅ Fase 1: Cimientos y Motores de Procesamiento Local
- [x] Establecer gobernanza, reglas de agentes y arquitectura (`AGENTS.md`, `GEMINI.md`, `SKILL.md`, `docs/`).
- [x] Implementar motor de extracción tabular (`TabularExtractor` con `pandas`, `openpyxl`, `csv`).
- [x] Implementar motor de extracción PDF (`PDFExtractor` con `PyMuPDF` y `pdfplumber`).
- [x] Implementar motor de reglas y extracción de entidades (`RuleExtractor` con `regex`).
- [x] Implementar clasificador de documentos ML clásico (`MLClassifier` con `scikit-learn` TF-IDF).
- [x] Crear suite de pruebas unitarias exhaustivas con casos borde y sanitización de inyección de fórmulas CSV.

### ✅ Fase 2: Backend API, Persistencia Local & Arquitectura sin Docker
- [x] Modelos SQLAlchemy multi-tenant (`Organization`, `User`, `Document`, `ExtractionRecord`, `SchemaDefinition`).
- [x] Motor de persistencia asíncrono con **SQLite Asíncrono (`sqlite+aiosqlite`)** y compatibilidad con PostgreSQL.
- [x] Almacenamiento local aislado en disco con protección contra path traversal (`LocalStorageService`).
- [x] Pipeline asíncrono en segundo plano (`FastAPI BackgroundTasks`) para procesamiento no bloqueante.
- [x] Endpoints REST para `/health`, `/upload`, `/documents/{id}`, `/documents` y `/extract`.
- [x] Scripts de inicio rápido para Windows (`start_backend.ps1`).

### ✅ Fase 3: Frontend Dashboard & Visualizador Interactivo
- [x] Aplicación Next.js 14+ (App Router), TypeScript y Tailwind CSS.
- [x] Studio de subida interactivo con soporte *Drag & Drop* y validación en cliente.
- [x] Dashboard con métricas de archivos procesados, estados y nivel de privacidad.
- [x] Visualizador de tablas complejas con soporte multi-hoja, buscador en vivo por celdas y cuadrícula de campos normalizados.
- [x] Exportador instantáneo a formatos limpios CSV y JSON estructurado.
- [x] Script de inicio para frontend (`start_frontend.ps1`).

### ✅ Fase 4: Generador de Documentos de Negocio
- [x] Script generador en Python (`scripts/generate_sample_documents.py`).
- [x] 6 documentos de prueba realistas generados en `samples/` (Factura Excel, Inventario CSV, Pedido CSV, Nómina Excel, Factura PDF, Contrato PDF).
- [x] Suite de pruebas automatizadas integradas (`tests/test_generated_samples.py`).

### ✅ Fase 5: Motor de Esquemas Canónicos & Mapeo Visual de Columnas
- [x] Modelo de datos `SchemaDefinition` y 4 plantillas de esquema estándar (Facturas, Inventario, Órdenes de Compra, Nóminas).
- [x] Motor de asignación óptima voraz con coincidencia difusa (`rapidfuzz`) en `SchemaNormalizer`.
- [x] Normalizador tipado para monedas, fechas ISO y booleanos.
- [x] Gestor de esquemas en frontend (`/schemas`) con constructor dinámico de campos y alias.
- [x] Modal de mapeo interactivo (`SchemaMapperModal`) con sugerencias automáticas de afinidad y preview en tiempo real.
- [x] Suite de 22 pruebas automatizadas completada con 100% de éxito.

### ✅ Fase 6: Reglas de Automatización de Negocio & Webhooks Salientes
- [x] Modelo `AutomationRule` con operadores deterministas (`gt`, `lt`, `gte`, `lte`, `eq`, `neq`, `contains`, `is_empty`, `not_empty`) y eventos `extraction_completed` / `normalization_completed`.
- [x] Motor de evaluación de reglas (`RuleEngine`) con normalización numérica (incluye decimales europeos) y coincidencia case-insensitive.
- [x] Disparador de **Webhooks HTTP salientes** hacia ERPs, Zapier, Make o n8n al completar la extracción o normalización (firma HMAC opcional, timeouts y reintentos configurables).
- [x] Registro de auditoría y trazabilidad de ejecuciones (`WebhookDelivery`) y test de envío por webhook.
- [x] CRUD completo de reglas y webhooks en la API y panel de gestión en el frontend (`/settings`).

### ✅ Fase 7: Autenticación, API Keys & Multi-Tenant RBAC
- [x] Autenticación de usuarios con JWT (HS256) y hashing seguro de contraseñas (PBKDF2-SHA256).
- [x] Generación de API Keys con prefijo `fm_` para ingesta desatendida mediante cURL y scripts externos (solo hash almacenado, rotación/revocación).
- [x] Roles de usuario (Admin, Member, Viewer), membresías por organización, selector de organizaciones en la interfaz y aislamiento estricto multi-tenant.
- [x] Página de inicio de sesión (`/login`) y guard de autenticación en el frontend.

---

## 🔮 Fases de Expansión Planificadas

### 📌 Fase 8: Suite de Escritorio & Agente de Bandeja (`PySide6 / Qt6`)
- [ ] Aplicación `FlowMind Desktop` con visor de PDF vectorial acelerado por hardware y tabla `QAbstractTableModel`.
- [ ] Agente de bandeja `Hot-Folder Tray Agent` con monitorización de carpetas (`watchdog`) y notificaciones nativas de Windows/Linux/macOS.
- [ ] `Visual Annotation Studio` para diseño gráfico interactivo de plantillas de extracción con cajas delimitadoras (`QGraphicsView`).
- [ ] Empaquetador ejecutable standalone con Nuitka/PyInstaller y edición portable para memorias USB.
- *Detalle técnico en:* [`docs/05-desktop-pyside6.md`](docs/05-desktop-pyside6.md)

### 📌 Fase 9: Visión Artificial Local, OCR & Documentos Escaneados
- [ ] Módulo OCR local integrado con `pytesseract` / `easyocr` para PDFs escaneados y fotos de tickets/facturas (`.png`, `.jpg`).
- [ ] Decodificador nativo de Códigos QR (TicketBAI, Veri\*factu, Swiss QR, SEPA EPC) y Códigos de Barras 1D (Code 128, EAN-13) con `pyzbar` / `zxing-cpp`.
- [ ] Detector óptico de marcas (*OMR*) con OpenCV para casillas marcadas/desmarcadas en partes de trabajo e inspección.
- [ ] Algoritmo de transformación de perspectiva (*Four-Point Dewarping*) y binarización adaptativa para fotos de móvil.
- *Detalle técnico en:* [`docs/06-advanced-engines.md`](docs/06-advanced-engines.md)

### 📌 Fase 10: Motor de Decisión, Grafo de Hechos & FlowMind Sentinel
- [ ] **Resolución de Entidades (`EntityResolutionEngine`)**: Unificación ponderada de variantes de proveedores y clientes con NIF, N-Grams y similitud difusa.
- [ ] **Validador Matemático Determinista (`MathematicalDocumentValidator`)**: Recálculo estricto de bases imponibles, cuotas de IVA, retenciones y totales generales con detección de desviaciones aritméticas.
- [ ] **FlowMind Sentinel (Antifraude)**:
  - *Bank Account Change Sentinel*: Alerta crítica y bloqueo ante cambios no autorizados de IBAN en facturas de proveedores.
  - *Detección Multidimensional de Duplicados*: Huella compuesta por NIF, número, fecha e importe.
  - *Detección de Evasión de Umbrales (*Threshold Avoidance*)* y análisis de distribución de *Ley de Benford*.
- [ ] **Grafo de Hechos Locales (`FactGraphEngine` con `NetworkX`)**: Vinculación relacional de Proyectos, Pedidos (PO), Albaranes (GR), Facturas y Pagos.
- [ ] **Decision Fabric & Aprobación a Cuatro Ojos (*Four-Eyes*)**: Enrutamiento por puntuación compuesta de confianza y segregación de funciones (*SoD*).
- *Detalle técnico en:* [`docs/08-enterprise-decision-engine.md`](docs/08-enterprise-decision-engine.md)

### 📌 Fase 11: Búsqueda Semántica Local & Memoria Documental Offline
- [ ] Motor de búsqueda semántica en lenguaje natural 100% offline utilizando embeddings cuantizados ONNX `MiniLM` y `FAISS`.
- [ ] Detección de duplicados cuasi-idénticos y revisiones de contratos mediante *SimHash* (distancia Hamming).
- [ ] *PII Redactor*: Anonimizador local de DNI, IBAN, emails y teléfonos antes de exportar o compartir documentos.
- *Detalle técnico en:* [`docs/07-local-search-and-compliance.md`](docs/07-local-search-and-compliance.md)

### 📌 Fase 12: Cumplimiento Fiscal, Inmutabilidad & Conectores ERP
- [ ] Generador de ficheros XML oficiales para el **SII de la AEAT** (Libros registro de facturas expedidas y recibidas).
- [ ] Sellado encadenado inmutable de facturas (*Tamper-Evident Hash Chaining*) para cumplimiento de la Ley Antifraude / *Veri\*factu*.
- [ ] Ingesta desatendida por correo electrónico (conectores IMAP / Microsoft Graph API).
- [ ] Conectores de integración directa para ERPs (Odoo XML-RPC, SAP Business One, A3ERP, Sage).
