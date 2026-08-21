¡Hola, equipo! Como su mentor y lead técnico, vamos a elevar el listón. Tienen un sprint de **3 días** para ejecutar estos proyectos con mentalidad de ingenieros senior.

No estamos buscando código copiado de foros ni soluciones superficiales que fallen al primer caso de borde. El objetivo es la **eficiencia, el entendimiento profundo del problema y la arquitectura limpia**, usando Python y capacidades de Inteligencia Artificial.

---

### Organización del Equipo (3 Integrantes)

Para cada proyecto, deben distribuir obligatoriamente estos 3 roles:

1. **Backend & Core Engineer:** Responsable de la lógica de negocio, robustez de la aplicación, bases de datos y gestión de estados.
2. **AI & Data Pipeline Architect:** Responsable de la integración con los modelos de IA, flujos de procesamiento de datos, optimización y estrategia de ingesta/contexto.
3. **Frontend & Integration Lead:** Responsable de la interfaz de usuario, experiencia interactiva, validación de flujos y sincronización entre la App y la Automatización.

---

### Entregables a Nivel Gerencial (Obligatorios para cada proyecto)

Al finalizar los 3 días, cada grupo debe entregar un reporte ejecutivo que incluya:

1. **Diagrama de Arquitectura de Solución:** Visualización de cómo interactúan la App, la Automatización y la capa de Inteligencia Artificial.
2. **Matriz de Riesgos Técnicos y Mitigación:** Identificación de fallos potenciales (latencia, costos de tokens, alucinaciones, caídas de servicio) y su contención.
3. **Definición de Hecho (DoD) y Criterios de Aceptación:** Checklist técnico y funcional que valida que el sistema está listo para producción.
4. **Análisis de Eficiencia y Elección Tecnológica:** Justificación fundamentada de por qué decidieron usar IA local o en la nube, y cómo estructuraron la gestión de datos/contexto.
5. **Informe de Validación y Métricas de Impacto:** Demostración de cómo el sistema resuelve el problema operativo planteado usando casos de prueba reales.

---

## Los 6 Proyectos del Sprint

### Proyecto 1: Asistente Inteligente de Triaje y Enrutamiento de Soporte IT

* **El Problema:** El equipo de soporte técnico recibe cientos de tickets diarios con descripciones vagas, desorganizadas o incompletas de incidencias. Esto satura a los operadores y retrasa la atención crítica.
* **La App:** Una interfaz web interactiva donde el personal técnico visualiza la cola de tickets entrantes, su clasificación de prioridad sugerida, resumen ejecutivo del problema y una propuesta de respuesta preliminar para el usuario.
* **La Automatización:** Un proceso en segundo plano (background worker o pipeline programado) que monitorea una bandeja de entrada o webhook, ingesta nuevos reportes, procesa la información y la enriquece automáticamente antes de que un humano la toque.

### Proyecto 2: Auditor de Calidad de Código y Sincronizador de Documentación

* **El Problema:** Los equipos de desarrollo actualizan código constantemente, pero la documentación técnica y las guías internas quedan obsoletas rápidamente, generando deuda técnica invisible.
* **La App:** Un panel de control donde los desarrolladores pueden seleccionar un repositorio o conjunto de scripts, visualizar métricas de legibilidad, detectar funciones complejas y consultar un resumen automatizado de los cambios arquitectónicos recientes.
* **La Automatización:** Un script o tarea automatizada que se ejecuta periódicamente o ante eventos específicos, analiza la estructura de los archivos de código fuente, extrae la semántica y actualiza la base de conocimiento del equipo de forma autónoma.

### Proyecto 3: Navegador Inteligente de Políticas y Contratos Internos

* **El Problema:** Los empleados de una compañía pierden horas buscando información específica dentro de manuales de recursos humanos, contratos legales y políticas internas densas y extensas.
* **La App:** Un centro de consultas interno donde cualquier colaborador puede hacer preguntas complejas en lenguaje natural y obtener respuestas precisas acompañadas de las fuentes exactas y fragmentos de los documentos originales consultados.
* **La Automatización:** Un pipeline de ingesta y sincronización que detecta cuando se añade o modifica un documento en un repositorio compartido, procesa el material, extrae fragmentos clave y mantiene actualizado el sistema de recuperación de información de la empresa.

### Proyecto 4: Extractor, Validador y Reconciliador de Facturas y Comprobantes

* **El Problema:** El departamento financiero procesa facturas en formato PDF o imágenes con diseños totalmente heterogéneos, requiriendo captura manual propensa a errores humanos.
* **La App:** Una interfaz de gestión financiera donde el equipo revisa documentos subidos, visualiza los campos extraídos estructurados (proveedor, ítems, impuestos, totales) y detecta anomalías o discrepancias de forma visual.
* **La Automatización:** Un observador de directorios (folder watcher) o conector de correo que detecta la llegada de nuevos comprobantes adjuntos, extrae la información clave, valida las reglas de negocio y alimenta automáticamente una base de datos o sistema contable.

### Proyecto 5: Central de Inteligencia de Contenido y Programación Omnicanal

* **El Problema:** Los creadores de contenido y equipos de marketing batallan para transformar una idea general en múltiples formatos optimizados para diferentes plataformas manteniendo una línea editorial coherente.
* **La App:** Un estudio creativo web donde el usuario ingresa una premisa básica y obtiene variantes optimizadas de contenido (hilos, artículos, boletines) listas para revisar, editar y aprobar.
* **La Automatización:** Un sistema de tareas programadas que toma los contenidos aprobados en la aplicación, adapta su formato técnico según los requerimientos de salida y los distribuye o programa automáticamente en canales externos.

### Proyecto 6: Monitor de Sentimiento de Clientes y Alertas de Riesgo de Abandono (Churn)

* **El Problema:** Las empresas reciben feedback masivo de clientes a través de reseñas, encuestas y chats de soporte, pero no logran detectar a tiempo señales críticas de insatisfacción o frustración severa.
* **La App:** Un tablero analítico en tiempo real que muestra la evolución del sentimiento de los usuarios, agrupa los principales puntos de fricción detectados y resalta casos de alto riesgo que requieren intervención inmediata.
* **La Automatización:** Un proceso automatizado que recopila periódicamente nuevas interacciones o reseñas de fuentes externas, analiza el contexto y las emociones subyacentes, y dispara alertas automatizadas cuando identifica patrones de riesgo crítico.