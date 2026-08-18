# FlowMind AI — Visión del Producto

## 1. Declaración de Misión y Filosofía

**FlowMind AI** es una plataforma SaaS B2B y suite de software diseñada para la **automatización inteligente de procesos empresariales y toma de decisiones operacionales**. Su misión es transformar información desestructurada y semi-estructurada (PDFs, hojas de cálculo Excel, CSVs, extractos bancarios e imágenes) en **hechos canónicos verificados, grafos relacionales de transacciones y acciones automatizadas con trazabilidad forense**.

La plataforma opera bajo el principio no negociable de **Zero Cloud Data Leakage (100% Local, Privada y Determinista)**:
- Cero transmisión de datos confidenciales o documentos a APIs externas de LLMs (OpenAI, Gemini, Anthropic).
- Procesamiento en el perímetro local mediante librerías de Python puras, NLP determinista (`rapidfuzz`, `regex`), visión artificial offline (`zxing-cpp`, `pytesseract`, `OpenCV`), grafos locales (`NetworkX`) y algoritmos clásicos de Machine Learning (`scikit-learn`).
- Predictibilidad operativa con latencias en milisegundos y cero coste marginal por inferencia.

---

## 2. Para Quién se Construye (Target Audience)

1. **Equipos Contables y Financieros (Procure-to-Pay):** Automatización de la conciliación a 3 vías (Pedido ↔ Albarán ↔ Factura), detección de sobrefacturación y validación matemática de impuestos.
2. **Dirección Financiera (CFO & Tesorería):** Detección continua de fraude (FlowMind Sentinel), verificación de cambios de IBAN, compliance fiscal (AEAT SII, Veri\*factu) y exportación SEPA.
3. **Equipos de Logística y Almacén:** Conciliación de albaranes de entrega física, seguimiento de transportistas y control de inventarios tabulares.
4. **Recursos Humanos y Nóminas:** Desagregación masiva de nóminas en PDFs confidenciales individuales y extracción de tickets de gastos.
5. **Empresas en Sectores Regulados o con Datos Confidenciales:** Banca, aseguradoras, salud, peritajes y auditoría donde la filtración de datos a servidores en la nube está estrictamente prohibida por ley o política interna.
