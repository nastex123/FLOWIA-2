# ADR-003: Cliente de Interfaz Principal en Suite de Escritorio PySide6 (Desktop-First)

* **ID:** ADR-003
* **Título:** Migración del cliente de interfaz a la suite de escritorio PySide6
* **Fecha:** 2026-08-18
* **Estado:** `Accepted & Executed` (Frontend Web retirado del repositorio)
* **Relacionados:** [ADR-001](ADR-001-local-deterministic-engine.md), [ADR-002](ADR-002-two-plane-architecture.md)

---

## Contexto

FlowMind AI necesita una interfaz de gestión financiera donde el equipo revise documentos subidos, visualice los campos extraídos estructurados (proveedor, ítems, impuestos, totales) y detecte anomalías o discrepancias de forma visual.

El estado real de los clientes en el repositorio era:

* **Frontend web (Next.js 14):** existía como andamiaje incompleto y roto sin `frontend/src/lib/`.
* **Suite de escritorio (PySide6 / Qt6):** base nativa funcional de alto rendimiento, coherente con los principios de privacidad local y entornos air-gapped del proyecto.

## Problema

El equipo necesita una app funcional para la tarea de "Extractor, Validador y Reconciliador de Facturas y Comprobantes" y debe decidir sobre qué cliente construirla: reparar el frontend web incompleto o consolidar el cliente al 100% en la suite de escritorio PySide6 eliminando el código web muerto.

## Opciones consideradas

| Opción | Ventajas | Desventajas |
| :--- | :--- | :--- |
| **A. Reparar frontend web Next.js** | Reutiliza componentes esbozados; acceso desde navegador | Requiere crear `src/lib/` completo; el proyecto prioriza entornos privados/air-gapped sin navegador; más superficie de dependencias |
| **B. Consolidar al 100% en PySide6 y eliminar frontend web** (elegida) | Alineado con "Zero Cloud Data Leakage" y air-gapped; el watcher hot-folder ya vive en escritorio; UI nativa de alto rendimiento para tablas masivas; cero dependencias de Node.js/npm | Requiere construir las pantallas de revisión financiera; app de escritorio (no accesible por navegador) |
| C. Mantener ambos | Máxima cobertura | Duplica mantenimiento; el frontend web estaba roto y añade sobrecarga técnica |

## Decisión

**El cliente de interfaz pasa a ser al 100% la suite de escritorio nativa PySide6 (Qt6)**, que actúa como cliente del backend FastAPI (persistencia, validación, reglas y webhooks). **El directorio `frontend/` y las dependencias de Node.js/npm se eliminan por completo del repositorio.**

## Justificación

1. **Alineación con la visión del producto:** la suite de escritorio es un pilar documentado (`docs/03-architecture/03-desktop-pyside6.md`) para entornos ultra-privados y air-gapped.
2. **El watcher de carpetas ya existe en escritorio:** la automatización hot-folder → backend se integra en el mismo cliente sin duplicar lógica.
3. **Rendimiento de UI:** tablas de ítems y reconciliación requieren `QTableView` + modelo virtual, coherentes con el grid de alto rendimiento ya diseñado.
4. **Eliminación de deuda técnica:** sin necesidad de mantener Node.js, npm, paquetes de react o servidores frontend secundarios.
5. El frontend web **no aportaba valor real** a la solución local offline.

## Consecuencias

* **Positivas:** app de gestión financiera nativa, rápida y privada; integración natural con hot-folder; sin servidor web adicional ni dependencias de Node.js; stack 100% Python.
* **Limitaciones:** la app se ejecuta de forma nativa en el sistema operativo (no desde navegador).
* **Acción ejecutada:** se eliminó el directorio `frontend/`, scripts relacionados y se actualizaron `install.py`, `start.py`, `README.md`, `AGENTS.md` y `CHANGELOG.md`.