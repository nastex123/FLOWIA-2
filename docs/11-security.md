# 11 — Directrices de Seguridad y Privacidad

Este documento define la política de seguridad, mitigación de riesgos y privacidad de datos de **FlowMind AI**.

---

## 1. Principio de Privacidad Local (Zero Cloud Data Leakage)

* **Sin Inferencia Externa:** Ningún documento, fragmento de texto o dato tabulado es transmitido a APIs externas de LLMs (OpenAI, Gemini, Anthropic).
* **Cumplimiento GDPR/RGPD:** Al procesar toda la información de forma estrictamente local dentro del perímetro de la infraestructura del cliente, se garantiza el cumplimiento normativo sin acuerdos de procesamiento de datos con proveedores de LLMs.

---

## 2. Validación y Sanitización de Archivos

Los archivos subidos por los usuarios son fuentes de datos no confiables.

### 2.1 Inspección de Cabeceras Mágicas (MIME Real)
No confiar en la extensión del archivo (`.pdf`, `.xlsx`, `.csv`). El sistema debe verificar las cabeceras binarias (ej. `%PDF-` para PDFs, firma PK/ZIP para `.xlsx`).

### 2.2 Prevención de Inyección de Fórmulas (CSV / Spreadsheet Formula Injection)
Al exportar o procesar archivos tabulares, cualquier celda que comience con `=`, `+`, `-`, `@`, `\t` o `\r` puede ser interpretada como una fórmula ejecutable por clientes como Excel.
* **Mitigación:** Prefijar dichas celdas con una comilla simple `'` o sanitizar el valor antes de procesarlo/exportarlo.

### 2.3 Protección contra DoS y Bombas de Descompresión
* Límite estricto de tamaño de subida (ej. 25 MB por defecto).
* Validación de recuento máximo de filas (`max_rows`) y columnas (`max_columns`) durante la carga en memoria con `pandas` / `openpyxl`.
* Timeout estricto en la extracción de PDFs para prevenir loops infinitos en documentos con capas corruptas.

---

## 3. Aislamiento Multi-Tenant

* **PostgreSQL:** Toda tabla que contenga datos corporativos debe incluir `organization_id` con índice.
* **Consultas:** Todas las operaciones de lectura, actualización y eliminación deben incluir la cláusula `WHERE organization_id = :current_org_id`.
* **Almacenamiento de Archivos:** Las rutas de almacenamiento aíslan los archivos por carpeta de organización:
  ```text
  /storage/{organization_id}/{document_id}/{filename}
  ```

---

## 4. Autenticación, API Keys y RBAC

* **Contraseñas:** Almacenadas con hash **PBKDF2-SHA256** (`hashlib.pbkdf2_hmac`, 310.000 iteraciones) y salt aleatorio por usuario; nunca en texto plano.
* **Tokens JWT:** Firmados con HMAC-SHA256 usando `SECRET_KEY` (variable de entorno). Expiración por defecto 24h (`JWT_EXPIRES_MINUTES`). El JWT solo contiene `sub` (user id), `role`, `org` y expiración.
* **API Keys:** Generadas con prefijo `fm_` y 32 bytes de entropía. Solo se persiste el hash SHA-256 del valor en claro; el secreto se muestra una única vez al crearlo. Rotación mediante revocación (`is_active=False`).
* **RBAC por Organización:** Roles `admin`, `member`, `viewer`. Las operaciones de escritura en reglas y webhooks están restringidas a `admin`; esquemas y API Keys a `admin`/`member`. Toda operación verifica la membresía del usuario en la organización del contexto (`X-Organization-Id`).

---

## 5. Webhooks Salientes y Datos Confidenciales

* Los webhooks salientes solo se envían a URLs **configuradas explícitamente** por un administrador de la organización.
* Si el webhook define un `secret`, cada petición incluye la cabecera `X-Webhook-Signature: sha256=<hmac>` firmando el cuerpo, para que el receptor valide autenticidad e integridad.
* Los secretos de webhook se almacenan cifrados a un solo lado (solo se expone `has_secret` en la API).
* El registro de auditoría (`webhook_deliveries`) guarda URL destino, estado, código HTTP y error, pero **nunca el cuerpo del documento enviado**.

---

## 6. Gestión de Secretos y Logging

* **Variables de Entorno:** Toda clave secreta (`SECRET_KEY`, credenciales de DB, Redis) se obtiene mediante `Pydantic Settings` desde variables de entorno.
* **Cero Secretos en Repositorio:** El archivo `.gitignore` excluye `.env`, certificados y archivos de credenciales.
* **Sanitización de Logs:** Los logs nunca deben imprimir:
  * Contraseñas o hashes.
  * Tokens JWT o cabeceras de autorización.
  * Datos personales identificables (PII) o contenido íntegro de documentos empresariales.
