# ADR-001: Procesamiento 100% Local y Determinista sin LLMs en la Nube

* **Fecha:** 2026-08-17
* **Estado:** `Accepted`
* **Contexto:** FlowMind AI procesa documentos empresariales de alta confidencialidad (facturas, balances contables, nóminas con salarios y DNI, contratos mercantiles). La integración de APIs de LLMs en la nube (como OpenAI GPT-4, Gemini o Claude) introduce graves riesgos de fuga de datos (Cloud Data Leakage), costes recurrentes impredecibles por token y latencias inaceptables en lotes masivos.
* **Decisión:** Desarrollar toda la inteligencia de extracción, clasificación y validación utilizando exclusivamente librerías de Python locales y deterministas (`pandas`, `PyMuPDF`, `rapidfuzz`, `scikit-learn`, `NetworkX`, `zxing-cpp`, `pytesseract`).
* **Justificación:**
  1. Garantía absoluta de cumplimiento normativo (RGPD / LOPD) sin requerir DPA con proveedores externos de IA.
  2. Latencia de procesamiento inferior a 100 ms por documento.
  3. Cero coste por consulta o procesamiento de documentos.
  4. Resultados 100% reproducibles y deterministas.
* **Consecuencias:**
  - *Positivas:* Máxima seguridad, viabilidad en entornos *Air-Gapped* / aislados, costes fijos predecibles.
  - *Limitaciones:* Menor flexibilidad en texto libre conversacional no estructurado; requiere diseño riguroso de reglas y pipelines de ML supervisado.
