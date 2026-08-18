# Arquitectura del Frontend Web (Next.js 14+ & Tailwind CSS)

Este documento detalla el diseño, estructura de componentes y flujo de datos de la interfaz de usuario de **FlowMind AI**, implementada como una **aplicación web moderna en Next.js (App Router, TypeScript, Tailwind CSS, Lucide Icons y Canvas Acelerado por GPU)**.

---

## 1. Motivación y Decisión Arquitectónica

Para superar las limitaciones de renderizado nativo, fuentes y composiciones complejas de ventanas de escritorio tradicionales, FlowMind AI migró su capa de presentación a una arquitectura **Web Frontend en Next.js 14+**:
* **Control total de diseño y animaciones:** Transiciones CSS puras (`transition-all duration-300`), efectos Glassmorphism (`backdrop-blur-xl`), paleta Gótica Obsidian & Crimson y sombras profundas.
* **Canvas de Geometría Sagrada a 60 FPS:** Renderizado vectorial acelerado por GPU de Rosetones de Catedral, círculos de compás alquímico y brasas ascendentes sin consumir hilos de Python.
* **Integración API REST transparente:** Cliente API en TypeScript con soporte para JWT, autenticación por cabeceras `X-Organization-Id`, `X-API-Key` y modo offline/demo simulado out-of-the-box.

---

## 2. Estructura de Directorios (`frontend/`)

```text
frontend/
├── package.json               # Dependencias: Next 14, React 18, Tailwind CSS, Lucide Icons
├── tsconfig.json              # Configuración TypeScript estricta (@/* paths)
├── tailwind.config.ts         # Paleta Obsidian (#030408), Crimson (#881337) y Amethyst
├── next.config.mjs            # Proxy rewrites (/api/v1/* -> http://127.0.0.1:8000/api/v1/*)
├── src/
│   ├── app/
│   │   ├── layout.tsx         # Root layout con GothicBackdrop canvas
│   │   ├── page.tsx           # Dashboard: KPIs, tabla de comprobantes y catálogo de sellos
│   │   ├── review/[id]/page.tsx # Workspace de revisión por pestañas y botón de consagración
│   │   ├── settings/page.tsx  # Configuración: umbrales Sentinel, Hot-Folder y claves API
│   │   ├── local/page.tsx     # Extracción local en 2 columnas y grilla tabular
│   │   └── login/page.tsx     # Cámara de autenticación JWT y Modo Cripta Offline
│   ├── components/
│   │   ├── GothicBackdrop.tsx # Canvas HTML5 con rosetón gótico rotatorio y partículas
│   │   ├── GothicGlyphs.tsx   # Catálogo de 24 figuras y sellos vectoriales
│   │   ├── GothicGlyphsGrid.tsx # Grilla interactiva de 24 figuras góticas
│   │   ├── GothicCornerOrnament.tsx # Esquineros de filigrana y forja
│   │   ├── GothicDivider.tsx  # Divisores de catedral con cruz radiante
│   │   ├── GothicArchWatermark.tsx # Ventanal ojival en marca de agua
│   │   ├── GothicRoseCircle.tsx # Rosetón rotatorio SVG dentro de tarjetas
│   │   ├── Sidebar.tsx        # Barra lateral colapsable (256px a 80px)
│   │   ├── Header.tsx         # Cabecera con selector multi-tenant y estado del santuario
│   │   ├── KpiCard.tsx        # Tarjeta KPI con borde iluminado
│   │   ├── DocumentTable.tsx  # Tabla con búsqueda, filtros y badges de severidad
│   │   └── FileUploadModal.tsx # Modal de ingesta con Drag & Drop
│   └── lib/
│       ├── api.ts             # Cliente API TypeScript conectando a FastAPI
│       ├── types.ts           # Definiciones de tipos TypeScript
│       └── mockData.ts        # Datos de prueba para modo demo offline
```

---

## 3. Puntos de Entrada y Ejecución

* **Lanzador Unificado:** `python start.py` (Inicia FastAPI en `:8000` y Next.js en `:3000`).
* **Frontend en Desarrollo:** `npm run dev` o `.\scripts\start_frontend.ps1`.
* **Build de Producción:** `npm run build`.
