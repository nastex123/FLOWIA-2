# ADR-003: Cliente de Interfaz Principal en Suite de Escritorio PySide6 (Desktop-First)

* **ID:** ADR-003
* **Título:** Migración del cliente de interfaz a la suite de escritorio PySide6
* **Fecha:** 2026-08-18
* **Estado:** `Accepted`
* **Relacionados:** [ADR-001](ADR-001-local-deterministic-engine.md), [ADR-002](ADR-002-two-plane-architecture.md)

---

## Contexto

FlowMind AI necesita una interfaz de gestión financiera donde el equipo revise documentos subidos, visualice los campos extraídos estructurados (proveedor, ítems, impuestos, totales) y detecte anomalías o discrepancias de forma visual.

El estado real de los clientes en el repositorio es:

* **Frontend web (Next.js 14):** existe como andamiaje incompleto. Importa módulos de `frontend/src/lib/` (`api`, `session`, `useAuthGuard`, `utils`) que **nunca fueron creados**, por lo que **no compila ni ejecuta**.
* **Suite de escritorio (PySide6 / Qt6):** existe una base funcional mínima (`MainWindow`, `VirtualDataTableModel`, `HotFolderWatcher`) que procesa localmente, coherente con los principios de privacidad local y entornos air-gapped del proyecto.

## Problema

El equipo necesita una app funcional para la tarea de "Extractor, Validador y Reconciliador de Facturas y Comprobantes" y debe decidir sobre qué cliente construirla: reparar el frontend web incompleto o migrar el cliente a la suite de escritorio PySide6.

## Opciones consideradas

| Opción | Ventajas | Desventajas |
| :--- | :--- | :--- |
| **A. Reparar frontend web Next.js** | Reutiliza componentes esbozados; acceso desde navegador | Requiere crear `src/lib/` completo; el proyecto prioriza entornos privados/air-gapped sin navegador; más superficie de dependencias |
| **B. Migrar cliente a PySide6** (elegida) | Alineado con "Zero Cloud Data Leakage" y air-gapped; el watcher hot-folder ya vive en escritorio; UI nativa de alto rendimiento para tablas masivas; sin servidor web adicional | Requiere construir las pantallas de revisión financiera; app de escritorio (no accesible por navegador) |
| C. Mantener ambos | Máxima cobertura | Duplica mantenimiento; el frontend web está roto y el equipo es de 4 personas |

## Decisión

**El cliente principal de la interfaz pasa a ser la suite de escritorio PySide6**, que actúa como cliente del backend FastAPI (persistencia, validación, reglas y webhooks). El frontend web Next.js queda **deprecated** (no se elimina en esta iteración; se marca como tal en la documentación y el roadmap).

## Justificación

1. **Alineación con la visión del producto:** la suite de escritorio es un pilar documentado (`docs/03-architecture/03-desktop-pyside6.md`) para entornos ultra-privados y air-gapped.
2. **El watcher de carpetas ya existe en escritorio:** la automatización hot-folder → backend se integra en el mismo cliente sin duplicar lógica.
3. **Rendimiento de UI:** tablas de ítems y reconciliación requieren `QTableView` + modelo virtual, coherentes con el grid de alto rendimiento ya diseñado.
4. **Menor coste de mantenimiento:** un único cliente principal en vez de dos, con el equipo actual de 4 personas.
5. El frontend web **no compila** hoy; su reparación completa no aporta valor adicional a la tarea asignada frente a la suite nativa.

## Consecuencias

* **Positivas:** app de gestión financiera nativa y privada; integración natural con hot-folder; sin servidor web adicional; menor superficie de dependencias.
* **Limitaciones:** requiere backend FastAPI corriendo (el cliente se conecta vía REST); la app no es accesible desde navegador; el frontend web queda sin mantenimiento (deprecated).
* **Acción derivada:** la documentación de clientes (`README.md`, `frontend/README.md`, roadmap) debe reflejar la deprecación del frontend web.