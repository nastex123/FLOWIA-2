
# 🚀 IA Team Sprint - Proyectos y Herramientas

Bienvenido al repositorio del sprint de Inteligencia Artificial y Automatización. Este documento centraliza la información sobre los proyectos asignados, los entregables esperados y las herramientas proporcionadas para el desarrollo.

## 📌 Contexto del Sprint
El equipo tiene **3 días** para desarrollar soluciones funcionales aplicando IA y Python. No buscamos prototipos rápidos ni código copiado; buscamos **eficiencia, arquitectura limpia y un entendimiento profundo del problema**. 

Cada grupo de 3 personas debe implementar una App y una Automatización de los proyectos listados, operando bajo roles específicos.

## 👥 Estructura del Equipo (Roles Obligatorios)
1. **Backend & Core Engineer:** Lógica de negocio, bases de datos y robustez del sistema.
2. **AI & Data Pipeline Architect:** Integración de LLMs, embeddings, RAG, manejo de contexto y *chunking*.
3. **Frontend & Integration Lead:** Interfaz de usuario, flujos interactivos y sincronización de datos.

## 🛠️ Herramienta de Soporte: Generador Mock (`generador_mock.py`)
Para evitar depender de datos de producción y facilitar las pruebas de carga, límites de tokens y estrategias RAG, hemos proporcionado un generador local de datos ficticios.

### Requisitos Previos
Asegúrate de instalar las dependencias necesarias antes de ejecutar el script:
```bash
pip install -r requirements.txt

```

### Uso

Ejecuta el script interactivo desde tu terminal:

```bash
python mock_generator.py

```

El menú te permitirá seleccionar qué conjunto de datos generar y la cantidad exacta que necesitas. Los resultados se guardarán automáticamente en la carpeta `mock_output/`.

### Datos Generados

* **P1 - Tickets de Soporte (Excel):** Casos técnicos densos con problemas reales simulados para probar extracción de entidades y clasificación.
* **P3 - Políticas Internas (HTML):** Documentos legales extensos con 3 layouts distintos para estresar los sistemas de parseo y las estrategias de *Chunking*.
* **P4 - Facturas (Excel):** Datos estructurados para flujos de validación financiera y reconocimiento de anomalías.

---

## 📋 Los Proyectos (Resumen)

Para ver el detalle completo, consulta el archivo `projects.md`

1. **[P1] Asistente de Triaje IT:** App de clasificación de tickets y automatización de enriquecimiento de datos de soporte.
2. **[P2] Auditor de Calidad de Código:** Dashboard de métricas de código y automatización de sincronización de documentación técnica.
3. **[P3] Navegador de Políticas Internas:** App de consultas RAG sobre documentos legales y automatización de actualización de la base de conocimiento ante nuevos archivos.
4. **[P4] Reconciliador de Facturas:** Interfaz de validación financiera y automatización de extracción de datos en PDFs/Imágenes.
5. **[P5] Central de Inteligencia Omnicanal:** Estudio de creación de variantes de contenido y automatización de distribución/programación.
6. **[P6] Monitor de Riesgo de Abandono (Churn):** Tablero de análisis de sentimiento y automatización de alertas críticas.

---

## 🎯 Entregables a Nivel Gerencial

Al finalizar los 3 días, independientemente del proyecto elegido, el equipo debe entregar:

1. **Diagrama de Arquitectura:** Visión técnica de la interacción App ↔ Automatización ↔ IA.
2. **Matriz de Riesgos:** Identificación y mitigación de fallos (costos, latencia, alucinaciones).
3. **Definición de Hecho (DoD):** Criterios de aceptación para pase a producción.
4. **Análisis de Eficiencia:** Justificación técnica de las herramientas elegidas (IA local vs Nube, RAG, etc).
5. **Métricas de Impacto:** Casos de prueba demostrando la resolución del problema.

---

*Si falla en desarrollo, arréglalo. Si falla en producción, explícalo. ¡Mucho éxito en el sprint!*
