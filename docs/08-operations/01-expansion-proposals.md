# Propuestas Estratégicas y Roadmap de Expansión Futura

Este documento consolida las **22 propuestas estratégicas y arquitectónicas** de alto impacto para la evolución de **FlowMind AI**, conservando los principios fundamentales de **Zero Cloud Data Leakage (100% Local)**, determinismo, Machine Learning clásico y alta velocidad sin dependencia de LLMs externos.

---

## 🎯 Bloque 1: Automatización Financiera & Tesorería (Procure-to-Pay)

### 1. Generador de Ficheros Bancarios SEPA XML (ISO 20022 - `pain.001` y `pain.008`)
* **Problema que resuelve:** Tras aprobar lotes de facturas, los equipos contables deben introducir manualmente una a una las transferencias en la banca electrónica.
* **Solución Técnica:** Generación automatizada de remesas de pago en formato XML estándar internacional ISO 20022 (`pain.001.001.03` para transferencias SEPA y `pain.008.001.02` para adeudos por domiciliación) con validación previa de IBANs mediante algoritmo MOD 97-10.
* **Categoría:** `RECOMENDADO`

### 2. Conciliador Multidivisa y Tipos de Cambio Históricos Offline
* **Problema que resuelve:** Facturas de importación/exportación en divisas extranjeras (USD, GBP, JPY) presentan diferencias de cambio entre la fecha de emisión/devengo y la fecha de liquidación o pago.
* **Solución Técnica:** Sincronización y almacenamiento local de la serie histórica de tipos de cambio oficiales de referencia del Banco Central Europeo (BCE), permitiendo el recálculo determinista de la base en EUR y el asiento de pérdidas/ganancias por diferencias de cambio.
* **Categoría:** `OPCIONAL`

### 3. Calculador de Amortizaciones y Asignación de Activos Fijos
* **Problema que resuelve:** Las compras de inmovilizado material o intangible (servidores, maquinaria, licencias) requieren cuadros de amortización contable periódicos según tablas oficiales.
* **Solución Técnica:** Motor de detección de bienes de inversión por concepto e importe que genera automáticamente el cuadro de amortización (lineal o degresiva) y el plan de cuotas periódicas para el ERP.
* **Categoría:** `FUTURO`

### 4. Gestor de Retenciones de Alquileres e IRPF Profesional (Modelos 111 / 115 / 190)
* **Problema que resuelve:** Las facturas de arrendamientos comerciales (19% IRPF) y servicios profesionales (15% o 7% IRPF) exigen declaraciones tributarias periódicas agregadas por perceptor.
* **Solución Técnica:** Clasificador especializado que acumula bases imponibles y retenciones por NIF de perceptor, generando los borradores estructurados listos para los modelos oficiales de la AEAT.
* **Categoría:** `RECOMENDADO`

---

## 🛡️ Bloque 2: Detección Avanzada de Fraude & Auditoría Forense (Sentinel Plus)

### 5. Análisis de Grafo de Conexiones Circulares y Conflicto de Intereses
* **Problema que resuelve:** Creación de proveedores instrumentales o sociedades ficticias por parte de empleados para adjudicarse compras o inflar precios.
* **Solución Técnica:** Uso de `NetworkX` para cruzar automáticamente en el grafo de hechos los identificadores, teléfonos, direcciones y cuentas bancarias de empleados contra la base canónica de proveedores.
* **Categoría:** `CRÍTICO`

### 6. Detector de Facturas Fantasma y Proveedores Inactivos
* **Problema que resuelve:** Pagos recurrentes a empresas extinguidas, dadas de baja en el censo o que reaparecen tras años sin actividad comercial previa.
* **Solución Técnica:** Puntuación de inactividad histórica y validación de reglas de control censal del CIF/NIF para bloquear pagos a sociedades en riesgo de disolución.
* **Categoría:** `RECOMENDADO`

### 7. Detector de Incoherencias en Secuencias de Numeración
* **Problema que resuelve:** Facturas emitidas fuera de orden cronológico o con saltos desmedidos.
* **Solución Técnica:** Verificación de monotonicidad temporal estricta en series de facturación emitidas y recibidas por proveedor.
* **Categoría:** `RECOMENDADO`

### 8. Sellador de Tiempo Local RFC 3161 (Local Time-Stamping Authority)
* **Problema que resuelve:** Acreditación fehaciente de la fecha y hora de recepción y procesamiento en entornos aislados.
* **Solución Técnica:** Emisión de sellos de tiempo criptográficos RFC 3161 integrados con la cadena inmutable de hashes locales.
* **Categoría:** `OPCIONAL`

---

## 📦 Bloque 3: Cadena de Suministro, Logística & Almacén

### 9. Extractor de Albaranes de Paquetería y Tracking OCR (GLS, SEUR, DHL, Correos)
* **Problema que resuelve:** Albaranes de entrega física con formatos heterogéneos y firmas manuscritas.
* **Solución Técnica:** Decodificación de códigos 1D/2D del transportista y extracción OCR de número de seguimiento, bultos y peso para conciliar la entrada en almacén.
* **Categoría:** `RECOMENDADO`

### 10. Optimizador de Control de Caducidades y Lotes en Almacén
* **Problema que resuelve:** Verificar que la vida útil de los lotes recibidos cumple las condiciones contractuales.
* **Solución Técnica:** Reglas de validación que analizan fecha de caducidad y número de lote frente a la vida útil mínima pactada.
* **Categoría:** `OPCIONAL`

### 11. Comparador de Tarifas de Proveedores y Detección de Inflación Oculta
* **Problema que resuelve:** Incrementos graduales o no comunicados en el coste unitario de artículos recurrentes (*creep inflation*).
* **Solución Técnica:** Análisis de series temporales por SKU que grafica la variación histórica de costes unitarios.
* **Categoría:** `RECOMENDADO`

---

## 👥 Bloque 4: Recursos Humanos & Gestión de Personal

### 12. Gestor de Tickets de Gastos de Empleados (*Expense Receipts OCR*)
* **Problema que resuelve:** Tickets de gastos arrugados o fotos móviles de baja calidad.
* **Solución Técnica:** Pipeline de preprocesamiento (Four-Point Dewarping + Binarización Sauvola + OCR) que extrae NIF, fecha, desglose de IVA y total.
* **Categoría:** `RECOMENDADO`

### 13. Verificador de Contratos de Trabajo y Plazos de Periodos de Prueba
* **Problema que resuelve:** Vencimiento imprevisto de periodos de prueba o contratos laborales temporales.
* **Solución Técnica:** Extracción determinista de cláusulas de duración, código de contrato y fechas de término con emisión de alertas.
* **Categoría:** `OPCIONAL`

---

## ⚙️ Bloque 5: Infraestructura, Conectividad & Canales de Ingesta

### 14. Ingestor Desatendido de Correo Electrónico IMAP / POP3 Local
* **Problema que resuelve:** Recepción masiva de facturas y documentos adjuntos por email.
* **Solución Técnica:** Servicio worker en segundo plano que sondea buzones de correo (IMAP seguro) y encola adjuntos validados en el pipeline.
* **Categoría:** `CRÍTICO`

### 15. Impresora Virtual FlowMind (Driver de Impresión Virtual PDF)
* **Problema que resuelve:** ERPs antiguos o programas legacy sin exportación de datos pero con soporte de impresión.
* **Solución Técnica:** Driver de impresora virtual para Windows/Linux que captura la salida gráfica y la envía a FlowMind.
* **Categoría:** `FUTURO`

### 16. Monitor de Carpetas Compartidas de Red SMB / NAS
* **Problema que resuelve:** Escáneres de oficina que depositan digitalizaciones en carpetas compartidas de red.
* **Solución Técnica:** Adaptador optimizado para `HotFolderWatcher` con soporte de rutas de red UNC.
* **Categoría:** `RECOMENDADO`

### 17. Modo Servidor Autónomo / Docker Compose de Producción
* **Problema que resuelve:** Despliegue centralizado on-premise en infraestructura corporativa.
* **Solución Técnica:** Configuración unificada con `docker-compose.yml`, PostgreSQL, Redis, FastAPI y Next.js.
* **Categoría:** `RECOMENDADO`

---

## 💻 Bloque 6: Experiencia de Usuario, Workbench & Formatos Estándar

### 18. Workbench de Corrección Asistida por Teclado a Alta Velocidad (Heads-Up Display)
* **Problema que resuelve:** La revisión manual con ratón es lenta en entornos de alta facturación.
* **Solución Técnica:** Interfaz de entrada rápida con pantalla dividida (visor PDF a la izquierda con zoom guiado por campo y formulario a la derecha), navegación 100% por teclado.
* **Categoría:** `RECOMENDADO`

### 19. Constructor Visual de Reglas de Negocio sin Código (No-Code Rule Builder)
* **Problema que resuelve:** Usuarios de negocio necesitan definir lógicas complejas sin programar.
* **Solución Técnica:** Constructor visual de bloques lógicos en el frontend que genera definiciones JSON deterministas.
* **Categoría:** `OPCIONAL`

### 20. Generador de Informes Ejecutivos de Ahorro y Eficiencia (ROI Dashboard)
* **Problema que resuelve:** Justificar ante la dirección financiera el valor tangible del sistema.
* **Solución Técnica:** Panel analítico que cuantifica horas ahorradas, dinero recuperado y reducción de tiempos de ciclo.
* **Categoría:** `RECOMENDADO`

### 21. Exportador Universal a Formatos Estándar Facturae 3.2.x y Factur-X / ZUGFeRD
* **Problema que resuelve:** Facturación electrónica B2B obligatoria en España y Europa.
* **Solución Técnica:** Generador y validador bidireccional para el estándar español **Facturae** (XML firmado XAdES) y el formato híbrido europeo **Factur-X / ZUGFeRD**.
* **Categoría:** `CRÍTICO`

### 22. Comparador Visual de Versiones de Documentos (Contract Diffing Pro)
* **Problema que resuelve:** Modificaciones sutiles de cláusulas entre versiones de contratos.
* **Solución Técnica:** Comparador geométrico y textual de PDFs que genera un mapa visual de diferencias superpuestas.
* **Categoría:** `OPCIONAL`
