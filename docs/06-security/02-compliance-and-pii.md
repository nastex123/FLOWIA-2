# Cumplimiento Fiscal, Búsqueda Local y Anonimización PII

Este documento define la arquitectura técnica del módulo de **cumplimiento fiscal (SII / Veri\*factu)**, **búsqueda semántica offline** y **protección de datos personales (PII / RGPD)** en **FlowMind AI**.

---

## 1. Cumplimiento Fiscal & Normativo (España / UE)

### 1.1 Módulo SII — Suministro Inmediato de Información (AEAT)
* **Objetivo:** Generación del XML oficial para el suministro inmediato de información de facturas emitidas y recibidas.
* **Componente:** `SIIGenerator` genera los bloques XML conformes a las especificaciones técnicas del portal de la Agencia Tributaria española (AEAT).

### 1.2 Encadenamiento Inmutable de Facturas (*Veri\*factu / TicketBAI*)
* **Objetivo:** Cumplimiento del Reglamento de requisitos de los sistemas informáticos de facturación (RD 1007/2023).
* **Componente:** `VerifactuEngine` genera el hash SHA-256 encadenado y la URL estructurada para código QR fiscal:
  $$\text{Hash}_{n} = \text{SHA-256}\Big(\text{Hash}_{n-1} \,\|\, \text{CIF} \,\|\, \text{NumFactura} \,\|\, \text{FechaHora} \,\|\, \text{ImporteTotal} \,\|\, \text{CuotaIVA}\Big)$$

---

## 2. Anonimizador y Redactor de Datos Sensibles (`PIIRedactor`)

* **Detección Determinista:** DNI/NIE/CIF españoles, códigos IBAN internacionales (con validación de checksum), direcciones de correo electrónico y números telefónicos.
* **Modos de Redacción:** Enmascaramiento parcial con caracteres comodín (ej. `*`), pseudonimización determinista por hash y marcado de cajas de redacción permanente en PDFs vectoriales.

---

## 3. Búsqueda Semántica Vectorial Local (Fase Planificada)

* Embeddings cuantizados INT8 del modelo `all-MiniLM-L6-v2` ejecutados en CPU con `onnxruntime`.
* Búsqueda por similitud coseno e índice local `FAISS` aislado por organización.
