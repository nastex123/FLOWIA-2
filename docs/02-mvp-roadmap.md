# 02 — Roadmap de Desarrollo del MVP

Este documento define el estado de avance y las fases de entrega del **MVP de FlowMind AI**.

---

## Objetivo del MVP

Construir un sistema B2B completo, autónomo y privado que permita a empresas subir archivos (Excel, CSV o PDF), procesarlos localmente mediante librerías de Python sin dependencias de LLMs externos, extraer tablas y campos clave de forma determinista, estandarizarlos mediante esquemas canónicos y visualizarlos en una interfaz moderna.

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

---

## 🔮 Próximos Hitos

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
