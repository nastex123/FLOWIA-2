# FlowMind AI — Frontend

> **⚠️ DEPRECATED** — Este frontend web (Next.js) queda **sin mantenimiento** desde el 2026-08-18. El cliente de interfaz principal es la **suite de escritorio PySide6** (ver [`docs/09-decisions/ADR-003-desktop-first-ui.md`](../docs/09-decisions/ADR-003-desktop-first-ui.md)). El código permanece en el repositorio a efectos de referencia; no se ampliará ni reparará en esta iteración.

Interfaz web para la gestión de documentos empresariales, visualización de tablas extraídas y configuración de esquemas de datos.

## Pila Tecnológica
* **Next.js 14+** (App Router)
* **React 18+**
* **TypeScript**
* **Tailwind CSS**

## Estructura Prevista
```text
frontend/
├── src/
│   ├── app/                # Páginas y layouts de Next.js
│   ├── components/         # Componentes UI reutilizables (Tablas, Upload, Modal)
│   ├── lib/                # Clientes API y utilidades
│   └── types/              # Definiciones TypeScript compartidas
├── public/                 # Assets estáticos
├── package.json
└── tailwind.config.ts
```
