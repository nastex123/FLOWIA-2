# Roadmap de Desarrollo y Fases de Entrega

Este documento define el estado de avance, los componentes completados y las fases de entrega de **FlowMind AI**.

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

### ✅ Fase 3: Suite de Gestión Financiera & Auditoría Desktop (`PySide6 / Qt6`)
- [x] Interfaz de usuario nativa de alto rendimiento en PySide6 (Qt6) con Dark Theme moderno y paleta Slate.
- [x] Visor de facturas y comprobantes con tarjetas KPIs de auditoría en tiempo real y buscador instantáneo.
- [x] Modelo de tabla virtual (`VirtualDataTableModel`) con badges coloreados de severidad de anomalías (`critical`, `warning`, `info`, `ok`).
- [x] Detalle de factura estructurada en 2 columnas: metadatos de cabecera, tabla de ítems, recálculo de IVA y panel lateral de hallazgos (`document_checks`).
- [x] Acción "Marcar como revisada" conectada a `POST /documents/{id}/review`.
- [x] Diálogo de autenticación JWT con selector de organizaciones y acceso directo a "Modo Demo Offline".
- [x] Suite de 13 pruebas automatizadas de interfaz y contrato API en verde.

### ✅ Fase 4: Generador de Documentos de Negocio
- [x] Script generador en Python (`scripts/generate_sample_documents.py`).
- [x] 6 documentos de prueba realistas generados en `samples/` (Factura Excel, Inventario CSV, Pedido CSV, Nómina Excel, Factura PDF, Contrato PDF).
- [x] Suite de pruebas automatizadas integradas (`tests/test_generated_samples.py`).

### ✅ Fase 5: Motor de Esquemas Canónicos & Normalización
- [x] Modelo de datos `SchemaDefinition` y 4 plantillas de esquema estándar (Facturas, Inventario, Órdenes de Compra, Nóminas).
- [x] Motor de asignación óptima voraz con coincidencia difusa (`rapidfuzz`) en `SchemaNormalizer`.
- [x] Normalizador tipado para monedas, fechas ISO y booleanos.
- [x] Extracción y normalización estructurada automática (`InvoiceStructurizer`).

### ✅ Fase 6: Reglas de Automatización de Negocio & Webhooks Salientes
- [x] Modelo `AutomationRule` con operadores deterministas (`gt`, `lt`, `gte`, `lte`, `eq`, `neq`, `contains`, `is_empty`, `not_empty`) y eventos `extraction_completed` / `normalization_completed`.
- [x] Motor de evaluación de reglas (`RuleEngine`) con normalización numérica.
- [x] Disparador de **Webhooks HTTP salientes** hacia ERPs o herramientas de automatización con firma HMAC opcional.
- [x] Registro de auditoría y trazabilidad de ejecuciones (`WebhookDelivery`).

### ✅ Fase 7: Autenticación, API Keys & Multi-Tenant RBAC
- [x] Autenticación de usuarios con JWT (HS256) y hashing seguro de contraseñas (PBKDF2-SHA256).
- [x] Generación de API Keys con prefijo `fm_` para ingesta desatendida mediante cURL y scripts externos.
- [x] Roles de usuario (Admin, Member, Viewer), membresías por organización y aislamiento estricto multi-tenant.

---

## 🔮 Fases de Expansión y Estado de Componentes

### 📌 Fase 8: Automatización Hot-Folder & Herramientas de Despliegue
- [x] Instalador automatizado multiplataforma sin dependencias externas (`install.py` con soporte Windows/Linux/macOS y smoke tests).
- [x] Lanzador unificado multiplataforma (`start.py`, `start.ps1`, `start.sh`) con autodetección de puertos y apagado coordinado.
- [x] Agente de monitorización de carpetas en segundo plano (`HotFolderWatcher` con `watchdog`).
- [x] Conexión del `HotFolderWatcher` al backend vía `POST /documents/upload` con API Key (Beatriz - Tarea P4a).
- [x] Pantalla de configuración del agente (`desktop/ui/settings_view.py` - Beatriz - Tarea P4a).
- [ ] Empaquetador ejecutable standalone con Nuitka/PyInstaller y edición portable para memorias USB.

### 📌 Fase 9: Visión Artificial Local, OCR & Códigos 1D/2D
- [x] Decodificador nativo de Códigos QR (TicketBAI, Veri\*factu, Swiss QR) y Barcodes 1D (Code 128, EAN-13) con `zxing-cpp` y `pyzbar`.
- [x] Detector óptico de marcas (*OMR*) con OpenCV para casillas marcadas/desmarcadas.
- [x] Algoritmo de transformación de perspectiva (*Four-Point Dewarping*) y binarización adaptativa para fotos de móvil.
- [x] Módulo OCR local integrado con `pytesseract` para PDFs escaneados e imágenes.
- [ ] Conexión del preprocesador de visión al inicio del pipeline desatendido en `/documents/upload`.

### 📌 Fase 10: Motor de Decisión, Grafo de Hechos & FlowMind Sentinel
- [x] **Resolución de Entidades (`EntityResolutionEngine`)**: Unificación ponderada de variantes de proveedores y clientes con NIF, N-Grams y similitud difusa.
- [x] **Validador Matemático Determinista (`MathematicalDocumentValidator`)**: Recálculo estricto de bases imponibles, cuotas de IVA, retenciones y totales generales con detección de desviaciones aritméticas.
- [x] **FlowMind Sentinel (Antifraude)**:
  - *Bank Account Change Sentinel*: Alerta crítica y bloqueo ante cambios no autorizados de IBAN en facturas de proveedores.
  - *Detección Multidimensional de Duplicados*: Huella compuesta por NIF, número, fecha e importe.
  - *Análisis de distribución de Ley de Benford* y detección de patrones de evasión.
- [x] **Grafo de Hechos Locales (`FactGraphEngine` con `NetworkX`)**: Vinculación relacional de Pedidos (PO), Albaranes (GR), Facturas y Pagos.
- [x] **Conciliación 3 Vías (`ThreeWayMatchingEngine`)**: Conciliación de cantidades y precios unitarios entre PO, GR e INV.
- [x] **Parser Bancario Norma 43 (`Norma43Parser`)**: Extracción estructurada de extractos bancarios españoles.
- [x] **Desagregador de Nóminas (`PayrollSplitter`)**: Segmentación de PDFs masivos de nóminas por empleado.
- [x] **Persistencia en Base de Datos**: Modelos `DocumentCheck`, `EntityRecord`, `InvoiceFingerprint` y migración Alembic (Luis - P1/P2).
- [x] Orquestación final del vertical completo y consolidación de contratos (Hector - Tarea P4b).

### 📌 Fase 11: Búsqueda Semántica Local & Anonimización PII
- [x] *PII Redactor*: Anonimizador local de DNI, IBAN, emails y teléfonos antes de exportar o compartir documentos (`PIIRedactor`).
- [ ] Motor de búsqueda semántica en lenguaje natural 100% offline utilizando embeddings cuantizados ONNX `MiniLM` y `FAISS`.
- [ ] Detección de duplicados cuasi-idénticos y revisiones de contratos mediante *SimHash* (distancia Hamming).

### 📌 Fase 12: Cumplimiento Fiscal, Inmutabilidad & Conectores ERP
- [x] Generador de ficheros XML oficiales para el **SII de la AEAT** (`SIIGenerator`).
- [x] Sellado encadenado inmutable de facturas (*Tamper-Evident Hash Chaining*) para cumplimiento de la Ley Antifraude / *Veri\*factu* (`VerifactuEngine`).
- [ ] Ingesta desatendida por correo electrónico (conectores IMAP / Microsoft Graph API).
- [ ] Conectores de integración directa para ERPs (Odoo XML-RPC, SAP Business One, A3ERP, Sage).

