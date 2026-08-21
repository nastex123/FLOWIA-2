# Pitch Técnico Ejecutivo — FlowMind AI (Proyecto 4)

**Proyecto:** FlowMind AI — Extractor, Validador y Reconciliador de Facturas y Comprobantes  
**Sprint:** 3 Días · Arquitectura Senior · Pure Python & Local AI (Zero Cloud Data Leakage)  
**Equipo:** Hector (Lead/AI), Luis (Backend Core/API), Brandon (Frontend/UX), Beatriz (Automatización/Watcher)

---

## 1. Ficha del Proyecto & Estructura del Equipo

| Integrante | Rol en el Sprint | Responsabilidades Principales |
| :--- | :--- | :--- |
| **Hector** | **Lead Architect & AI Pipeline Lead** (Orquestador) | Arquitectura de IA local, coordinación del equipo, análisis de riesgos y métricas de impacto. |
| **Luis** | **Backend & Core Engineer** (P1 + P2) | Dominio `StructuredInvoice`, `InvoiceStructurizer`, persistencia SQLAlchemy/Alembic y API REST de revisión. |
| **Brandon** | **Frontend & Integration Lead** (P3) | Interfaz web Next.js 14+, panel visual de anomalías, desglose de impuestos e inspección en tiempo real. |
| **Beatriz** | **Automation & Infrastructure Engineer** (P4a) | Agente Hot-Folder (`watchdog`), autenticación vía API Key, ingesta asíncrona y sincronización con base de datos. |

---

## 2. Guion del Pitch Técnico (Paso a Paso por Persona)

**Duración recomendada:** 5 a 6 minutos en total.

```text
[TIEMPO SUGERIDO: 6 MINUTOS TOTALES]
├── 0:00 - 1:00 | Hector: Introducción, Problema de Negocio y Enfoque Arquitectónico
├── 1:00 - 2:30 | Luis: Dominio Canónico, Structurizer Difuso, Sentinel y Backend API
├── 2:30 - 3:45 | Brandon: Experiencia de Usuario, Dashboard y Detección Visual de Anomalías
├── 3:45 - 4:45 | Beatriz: Automatización Hot-Folder, Ingesta Asíncrona y Conectividad
└── 4:45 - 6:00 | Hector: Métricas de Impacto, Q&A Técnico y Cierre Gerencial
```

---

### Bloque 1: Introducción, Problema y Filosofía de Diseño
**Voz:** **Hector** *(Lead Architect & Team Coordinator)* — `[0:00 - 1:00]`

> *"Buenos días a todos. En los departamentos financieros y contables, el procesamiento de facturas y comprobantes enfrenta un problema crítico: documentos heterogéneos en PDF, imágenes escaneadas o tablas de cálculo complejas donde la captura manual no solo es lenta, sino propensa a errores que derivan en pagos duplicados o discrepancias fiscales.*
>
> *Para resolverlo, construimos **FlowMind AI**. Nuestra propuesta técnica no es un envoltorio superficial alrededor de APIs en la nube. Frente a la tendencia de enviar información financiera confidencial a servidores de terceros, adoptamos un enfoque **100% Local y con Privacidad por Diseño (Zero Cloud Data Leakage)**.*
>
> *Desarrollamos una arquitectura modular que combina procesamiento determinista con Machine Learning clásico y visión offline, garantizando cero costo por token, latencias de procesamiento menores a 50 milisegundos y determinismo aritmético total. El sistema está validado por **115 pruebas automatizadas al 100%**. Doy paso a Luis para que detalle el núcleo del backend."*

---

### Bloque 2: Backend Core, Structurizer y Endpoints de Revisión
**Voz:** **Luis** *(Backend & Core Engineer)* — `[1:00 - 2:30]`

> *"Gracias, Hector. En la capa de Backend y lógica de negocio, mi objetivo fue estructurar y auditar la información sin tolerancia a alucinaciones.*
>
> *Diseñé el modelo canónico `StructuredInvoice` usando Pydantic v2 y SQLAlchemy Asyncio, acompañado de una migración Alembic que añade soporte para hallazgos (`DocumentCheck`), entidades (`EntityRecord`) y huellas criptográficas (`InvoiceFingerprint`).*
>
> *Cuando un documento es procesado, el motor `InvoiceStructurizer`:*
> 1. *Ejecuta matching difuso con `rapidfuzz` sobre cabeceras y columnas tabulares con un umbral estricto ($\ge 0.70$).*
> 2. *Normaliza Unicode, limpia monedas y extrae el desglose impositivo agrupado por tramos de IVA.*
> 3. *Ejecuta la validación matemática determinista, detectando desviaciones entre ítems, bases imponibles y el total impreso.*
> 4. *El motor Sentinel calcula la huella SHA-256 de la factura para prevenir duplicados y audita cambios no verificados en el IBAN o cuenta bancaria del proveedor.*
>
> *Expuse estos datos mediante endpoints REST enriquecidos (`/documents`, `/documents/{id}` y `/decision/checks`) con agregación de severidades (`ok`, `warning`, `critical`, `info`), acción de revisión (`POST /review`) y aislamiento multi-tenant obligatorio en cada consulta. Ahora Brandon mostrará la experiencia de usuario."*

---

### Bloque 3: Frontend Web, Inspección Visual y Detección de Anomalías
**Voz:** **Brandon** *(Frontend & Integration Lead)* — `[2:30 - 3:45]`

> *"Para que el equipo de finanzas interactúe con esta inteligencia de forma intuitiva, desarrollamos una suite web moderna con **Next.js 14 (App Router) y Tailwind CSS**.*
>
> *El dashboard central ofrece visibilidad inmediata del estado de la cola documental mediante tarjetas de KPI que resumen facturas procesadas, pendientes y alertas críticas. Al ingresar a la vista de inspección de factura (`/review/[id]`):*
> * *El auditor observa los metadatos completos del emisor, receptor, fechas y moneda.*
> * *La tabla estructurada de ítems muestra cantidades, precios unitarios, descuentos y tasas impositivas.*
> * *El panel lateral de auditoría resalta de forma cromática cada anomalía detectada por Sentinel o el validador matemático.*
> * *Con un solo clic en 'Marcar como Revisada', la factura pasa al estado `reviewed`, confirmando los hallazgos en la base de datos.*
>
> *Adicionalmente, implementamos un 'Modo Demo Offline' con datos realistas para demostraciones inmediatas y pruebas de contingencia. Le doy la palabra a Beatriz para explicar la automatización de entrada."*

---

### Bloque 4: Automatización Hot-Folder, Ingesta Asíncrona y Watcher
**Voz:** **Beatriz** *(Automation & Infrastructure Engineer)* — `[3:45 - 4:45]`

> *"Para que el sistema sea verdaderamente autónomo y no dependa de que un usuario suba archivos uno a uno, desarrollé el agente de bandeja **Hot-Folder Watcher** utilizando la librería `watchdog`.*
>
> *El agente monitorea carpetas locales o directorios de red compartidos donde escáneres o ERPs depositan comprobantes:*
> 1. *Filtra archivos temporales, ocultos o con extensiones no admitidas.*
> 2. *Inspecciona cabeceras MIME reales y previene ataques de inyección.*
> 3. *Transmite el archivo de forma asíncrona hacia el endpoint `POST /api/v1/documents/upload` autenticándose mediante cabeceras seguras `X-API-Key` y `X-Organization-Id`.*
> 4. *Si el servidor no está disponible, activa un modo de contingencia local que almacena la extracción JSON en una carpeta de salida.*
>
> *En cuanto el archivo cae en la carpeta, es ingerido, procesado y auditado en milisegundos, quedando disponible al instante en la pantalla de Brandon para su reconciliación contable."*

---

### Bloque 5: Métricas de Impacto, Análisis de Eficiencia y Cierre
**Voz:** **Hector** *(Lead Architect & Team Coordinator)* — `[4:45 - 6:00]`

> *"Para concluir, evaluemos el impacto y la eficiencia técnica de FlowMind AI:*
>
> *1. **Latencia y Rendimiento:** Procesamos y auditamos un comprobante en menos de 50 milisegundos, comparado con los 2 a 5 segundos que tardaría una llamada a un LLM en la nube.*  
> *2. **Costo Operativo:** Costo de inferencia igual a **cero dólares**, sin facturación por tokens ni cuotas de API.*  
> *3. **Privacidad y Cumplimiento:** Los datos fiscales y bancarios jamás abandonan la infraestructura local del cliente, cumpliendo estrictamente con GDPR y regulaciones financieras.*  
> *4. **Calidad de Código:** Logramos una cobertura integral con **115 pruebas automatizadas pasando**, cubriendo casos borde como facturas sin líneas de detalle, múltiples tramos de IVA, detección de duplicados y aislamiento multi-tenant.*
>
> *FlowMind AI demuestra que con una arquitectura limpia, librerías nativas de Python y un diseño centrado en el problema, es posible entregar una solución SaaS empresarial de alto valor en un sprint de 3 días. Quedamos a su disposición para sus preguntas."*

---

## 3. Matriz de Preguntas Frecuentes y Defensa Técnica (Q&A)

Si el mentor o lead técnico formula preguntas difíciles durante la presentación, utilicen estas respuestas fundamentadas:

### P1: ¿Por qué decidieron no usar un LLM (OpenAI / Claude / Gemini) para extraer las facturas?
* **Respuesta (Hector / Luis):** *"Por tres razones críticas en finanzas: **(1) Privacidad:** enviar facturas con datos bancarios (IBAN/CIF) a APIs externas viola políticas de privacidad empresarial; **(2) Determinismo:** los LLMs sufren de alucinaciones aritméticas y no garantizan que la suma de ítems coincida con el total; **(3) Costos y Disponibilidad:** con `PyMuPDF`, `pdfplumber`, `rapidfuzz` y `scikit-learn`, procesamos a coste $0 por documento en menos de 50ms, funcionando 100% offline."*

### P2: ¿Cómo garantizan que una factura con formato desconocido o columnas desordenadas no rompa el sistema?
* **Respuesta (Luis):** *"El motor `InvoiceStructurizer` no depende de posiciones fijas de coordenadas. Emplea mapeo difuso basado en distancias de Levenshtein ponderadas (`rapidfuzz`) contra un corpus de sinónimos canónicos (`cantidad`, `precio`, `importe`, `tasa`, `subtotal`), complementado con normalización Unicode y extracción de tablas basada en la geometría vectorial de `pdfplumber`."*

### P3: ¿Cómo manejan la concurrencia y la escalabilidad del sistema?
* **Respuesta (Hector / Beatriz):** *"El backend utiliza FastAPI con endpoints asíncronos (`async/await`) sobre SQLAlchemy Asyncio y PostgreSQL/SQLite. El agente Hot-Folder opera en hilos independientes sin bloquear el ciclo de eventos, y el procesamiento pesado puede desacoplarse mediante Redis y workers distribuidos."*

### P4: ¿Cómo aseguran el aislamiento entre diferentes empresas u organizaciones?
* **Respuesta (Luis):** *"FlowMind AI aplica multi-tenancy nativo. Cada token JWT porta el `org_id` autenticado, y cada consulta a nivel de base de datos (`Document`, `DocumentCheck`, `InvoiceFingerprint`, `EntityRecord`) filtra obligatoriamente por `organization_id`. El acceso cruzado devuelve un 404 estricto sin revelar la existencia de recursos ajenos."*

---

## 4. Checklist de Validación para la Demostración en Vivo

- [x] Backend FastAPI corriendo en `http://127.0.0.1:8000` con documentación Swagger en `/docs`.
- [x] Frontend Web Next.js corriendo en `http://localhost:3000`.
- [x] Login funcional con `admin@flowmind.local` / `admin123` y selector de organizaciones.
- [x] Modo Demo Offline operativo con datos de ejemplo (AceroCorp, TechParts, LogiTrans).
- [x] Subida de archivo de factura (`.xlsx` o `.pdf`) y visualización de ítems extraídos.
- [x] Detección de discrepancias matemáticas y badges de severidad en la vista de revisión.
- [x] Botón 'Marcar como Revisada' actualizando el estado contable en tiempo real.
- [x] Suite de 115 tests ejecutada con comando `pytest tests/` con salida 100% verde.
