# Product Requirements Document (PRD) — FlowMind AI

## 1. Resumen Ejecutivo y Problema de Negocio

Las organizaciones empresariales reciben diariamente cientos de documentos transaccionales en formatos desestructurados (PDFs escaneados, fotos móviles) y semi-estructurados (hojas de cálculo Excel con cabeceras caóticas, ficheros CSV, extractos bancarios Norma 43).

El procesamiento manual genera:
* Elevado coste operativo en personal de administración y contabilidad.
* Errores humanos de tecleo e inconsistencias aritméticas en bases imponibles e impuestos.
* Vulnerabilidad crítica a fraudes de suplantación de proveedores (*CEO Fraud / IBAN Swap*).
* Riesgo legal y sanciones por incumplimiento de plazos de pago (Ley de Morosidad) o normativas fiscales (SII AEAT, Veri\*factu / TicketBAI).
* Riesgo severo de fuga de información confidencial hacia servidores de LLMs en la nube (*Cloud Data Leakage*).

**FlowMind AI** resuelve este problema mediante un procesador local y determinista que ingesta, extrae, normaliza, valida y decide sobre los hechos documentales sin enviar jamás un byte fuera del host.

---

## 2. Requisitos Funcionales (FR)

* **FR-01 (Ingesta Multicanal):** El sistema debe aceptar archivos XLSX, XLS, CSV, PDF vectorial, PDF escaneado e imágenes (PNG, JPG) mediante API REST, bandeja de sistema (*Hot-Folders*) y subida web.
* **FR-02 (Extracción Tabular & Reglas):** Extracción determinista de tablas completas de múltiples hojas y detección de campos clave (NIF/CIF, total, fecha, número de factura) mediante expresiones regulares compiladas.
* **FR-03 (Normalización Asistida por Similitud Difusa):** Auto-sugerencia voraz (`rapidfuzz`) de columnas desestructuradas contra esquemas canónicos tipados (monedas, fechas ISO, booleanos).
* **FR-04 (Validación Matemática):** Recálculo aritmético determinista de bases, tramos de IVA, recargos y retenciones, alertando de discrepancias $\Delta > 1.00$ €.
* **FR-05 (Auditoría Antifraude Sentinel):** Bloqueo inmediato ante cambios de IBAN no autorizados de proveedores, detección de duplicados multidimensionales y análisis de Ley de Benford.
* **FR-06 (Conciliación a 3 Vías):** Cruce automático por línea entre Pedido de Compra (PO), Albarán de Entrega (GR) y Factura (INV).
* **FR-07 (Cumplimiento Fiscal):** Generación de XML oficial para el SII de la AEAT y cálculo de cadenas de hash inmutables conforme a Veri\*factu (RD 1007/2023).
* **FR-08 (Despacho Automatizado):** Disparador de Webhooks HTTP salientes firmados criptográficamente (HMAC-SHA256) hacia ERPs o herramientas de automatización (Zapier, Make, n8n).

---

## 3. Requisitos No Funcionales (NFR)

* **NFR-01 (Privacidad Cero Nube - Zero Cloud Data Leakage):** 100% de la inferencia, parsing y validación debe ejecutarse en local sin depender de APIs de terceros (OpenAI, Gemini, Anthropic).
* **NFR-02 (Rendimiento & Latencia):** Procesamiento de documentos de menos de 100 páginas en $< 2.0$ segundos en CPU estándar.
* **NFR-03 (Aislamiento Multi-Tenant Estricto):** Toda consulta a base de datos y toda ruta en almacenamiento de archivos debe estar aislada por `organization_id`.
* **NFR-04 (Manejo de Errores Tipados):** Ninguna excepción genérica no controlada; respuestas de error formateadas en JSON con código y detalle contextual.

---

## 4. Personas y Casos de Uso

| Persona | Rol | Objetivo Principal |
| :--- | :--- | :--- |
| **Ana (Contable Senior)** | Operadora de Facturación | Eliminar el tecleo de facturas y conciliar pedidos vs albaranes con 1 clic. |
| **Carlos (CFO / Director Financiero)** | Decisor & Aprobador | Prevenir fraudes de facturación duplicada y cambios no autorizados de cuenta bancaria. |
| **Laura (Responsable de RRHH)** | Gestora de Personal | Desagregar el PDF mensual de nóminas masivas en ficheros individuales seguros por empleado. |
| **Mario (Auditor / Compliance)** | Inspector de Cumplimiento | Verificar el encadenamiento de facturas Veri\*factu y anonimizar datos personales (PII). |
