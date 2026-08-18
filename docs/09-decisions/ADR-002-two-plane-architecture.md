# ADR-002: Separación en Dos Planos: Document Plane y Decision Plane

* **Fecha:** 2026-08-17
* **Estado:** `Accepted`
* **Contexto:** El procesamiento de documentos tradicional se limita a extraer texto o tablas y guardarlos en una base de datos. Sin embargo, en el entorno empresarial es indispensable validar los datos, relacionarlos con transacciones previas (Pedidos, Albaranes) y evaluar riesgos de fraude antes de autorizar pagos.
* **Decisión:** Estructurar el backend en dos planos conceptuales y de ejecución desacoplados:
  1. **Document Plane:** Responsable de ingesta, OCR, decodificación de códigos QR/1D, extracción tabular y clasificación ML.
  2. **Decision & Sentinel Plane:** Responsable de resolución de entidades canónicas, grafos de hechos (`NetworkX`), recálculo matemático determinista y auditoría antifraude (cambio de IBAN, duplicados, Benford).
* **Justificación:** Permite modularidad estricta, testeabilidad unitaria de cada componente e independencia entre la capa de extracción de datos y la capa de lógica de negocio y toma de decisiones.
* **Consecuencias:**
  - *Positivas:* Arquitectura extensible, capacidad de sustituir o añadir extractores sin afectar las reglas de negocio ni el motor antifraude.
  - *Limitaciones:* Requiere modelos DTO tipados en Pydantic v2 bien definidos para la transferencia de datos entre planos.
