---
name: documentation
description: >-
  Enforces documentation standards and changelog updates. Use whenever code changes, refactors, bug fixes,
  or feature additions are made, ensuring all changes are accurately documented in CHANGELOG.md with
  type, what, why, and America/Bogota timestamp, and technical documentation in docs/.
---

# DOCUMENTATION SKILL

## 1. PRINCIPIO FUNDAMENTAL

Toda modificación realizada en el proyecto DEBE quedar documentada.

La documentación es parte del desarrollo, no una actividad opcional posterior.

Ningún cambio debe considerarse completo hasta que:

1. El código o artefacto haya sido modificado correctamente.
2. La documentación correspondiente haya sido actualizada.
3. `CHANGELOG.md` refleje el cambio realizado.
4. La documentación sea consistente con el estado real del proyecto.

Nunca documentes cambios que no hayan sido realizados realmente.

Nunca omitas deliberadamente un cambio realizado.


## 2. CHANGELOG OBLIGATORIO

Todo cambio realizado DEBE registrarse en:

`CHANGELOG.md`

Esto aplica sin excepciones a:

- Nuevas funcionalidades.
- Modificaciones de funcionalidades existentes.
- Correcciones de errores.
- Eliminación de funcionalidades.
- Cambios de arquitectura.
- Cambios de configuración.
- Cambios de dependencias.
- Cambios de seguridad.
- Cambios de rendimiento.
- Refactors relevantes.
- Cambios en APIs.
- Cambios en modelos de datos.
- Cambios relacionados con IA/LLM/MAE.
- Cambios en infraestructura.
- Cambios exclusivamente documentales cuando sean relevantes.

Cada entrada DEBE contener:

- Tipo.
- Descripción de QUÉ se hizo.
- Descripción de POR QUÉ se hizo.
- Fecha y hora de Colombia.

Formato obligatorio de fecha:

`YYYY-MM-DD HH:mm`

Zona horaria:

`America/Bogota`

Tipos permitidos:

- `Added`
- `Changed`
- `Fixed`
- `Removed`
- `Deprecated`
- `Security`
- `Refactor`
- `Performance`
- `Docs`

Ejemplo:

`[2026-08-17 19:30] [Added] Se añadió el procesamiento batch de archivos CSV para permitir procesar múltiples documentos en una única ejecución.`

`Motivo: reducir el tiempo operativo necesario para procesar lotes de documentos empresariales.`


## 3. DOCUMENTACIÓN TÉCNICA

Toda documentación técnica DEBE almacenarse dentro de:

`docs/`

Nunca disperses documentación técnica arbitrariamente por el proyecto.

La estructura debe organizarse según el tipo de información.

Estructura recomendada:

```text
docs/
├── 00-vision/
├── 01-product/
├── 02-business/
├── 03-architecture/
├── 04-engineering/
├── 05-ai/
├── 06-security/
├── 07-qa/
├── 08-operations/
├── 09-decisions/
└── 10-releases/
```

No es obligatorio crear todos los directorios inmediatamente.

Solo deben existir los directorios necesarios para el estado actual del proyecto.


## 4. PRODUCT DOCUMENTATION

La documentación de producto DEBE describir qué se está construyendo y para quién.

Puede incluir:

- PRD.
- Requisitos funcionales.
- Requisitos no funcionales.
- User Stories.
- Personas.
- Casos de uso.
- User Flows.
- Especificaciones de funcionalidades.
- Roadmap.
- Criterios de aceptación.

El PRD representa:

`QUÉ se construye + PARA QUIÉN + POR QUÉ`

No debe utilizarse el PRD como sustituto de documentación técnica.


## 5. ARCHITECTURE DOCUMENTATION

Los documentos arquitectónicos DEBEN describir:

- Arquitectura general.
- Componentes.
- Dependencias.
- Flujos de datos.
- Integraciones.
- Límites entre servicios.
- Persistencia.
- Seguridad.
- Escalabilidad.
- Decisiones arquitectónicas relevantes.

La arquitectura debe mantenerse sincronizada con la implementación real.

Si la arquitectura cambia significativamente, debe actualizarse la documentación correspondiente y registrar el cambio en `CHANGELOG.md`.


## 6. TECHNICAL DOCUMENTATION

La documentación técnica puede incluir:

- Technical Design Documents.
- API Specifications.
- Database Schema.
- Data Models.
- Infrastructure.
- Deployment.
- Configuration.
- Development Workflow.
- Coding Standards.
- Integration Specifications.

El TDD debe explicar:

`CÓMO se implementa`

El PRD debe explicar:

`QUÉ se necesita construir`

No mezclar ambos propósitos innecesariamente.


## 7. AI DOCUMENTATION

Todo componente relacionado con Inteligencia Artificial DEBE documentarse dentro de:

`docs/05-ai/`

Esto incluye:

- Modelos utilizados.
- Modelos locales.
- Proveedores externos.
- Prompts.
- RAG.
- Embeddings.
- Context Management.
- Evaluación.
- Guardrails.
- Fallbacks.
- Costos.
- Latencia.
- Límites.
- Arquitectura de agentes.
- Flujos de inferencia.
- Decisiones relacionadas con LLMs.

Para sistemas deterministas como MAE, debe documentarse explícitamente:

- Inputs.
- Outputs.
- Reglas.
- Algoritmos.
- Validaciones.
- Errores.
- Guardrails.
- Integración con LLM.
- Qué información puede y no puede generar el LLM.


## 8. ARCHITECTURE DECISION RECORDS

Toda decisión técnica o arquitectónica importante DEBE poder registrarse como ADR.

Los ADR deben almacenarse en:

`docs/09-decisions/`

Formato recomendado:

`ADR-NNN-titulo.md`

Cada ADR debe contener:

- ID.
- Título.
- Fecha.
- Estado.
- Contexto.
- Problema.
- Opciones consideradas.
- Decisión.
- Justificación.
- Consecuencias.

Estados permitidos:

- `Proposed`
- `Accepted`
- `Rejected`
- `Deprecated`
- `Superseded`

Ejemplo:

`ADR-001-mae-as-deterministic-engine.md`

Una decisión importante NO debe depender únicamente de comentarios dentro del código.


## 9. CHANGELOG VS ADR

No confundir ambos conceptos.

`CHANGELOG.md` responde:

"¿Qué cambió?"

`ADR` responde:

"¿Por qué decidimos hacerlo de esta manera?"

Por lo tanto, una modificación arquitectónica puede requerir ambos.

Ejemplo:

ADR:
"Se decidió utilizar MAE como motor determinista para operaciones financieras."

CHANGELOG:
"Se integró MAE como motor de cálculo para operaciones financieras."


## 10. SECURITY DOCUMENTATION

Todo cambio relacionado con seguridad DEBE documentarse.

Esto incluye:

- Authentication.
- Authorization.
- Multi-tenancy.
- Tenant isolation.
- Secrets.
- Encryption.
- Data protection.
- Input validation.
- Permissions.
- Audit logs.
- Security fixes.
- Vulnerabilities.

Los cambios críticos de seguridad deben utilizar el tipo:

`Security`

Nunca documentar secretos, contraseñas, API keys, tokens u otra información sensible.


## 11. DATABASE AND DATA DOCUMENTATION

Los cambios importantes en datos DEBEN documentarse.

Esto incluye:

- Nuevas tablas.
- Eliminación de tablas.
- Cambios de columnas.
- Índices.
- Relaciones.
- Migraciones.
- Nuevos modelos.
- Cambios de serialización.
- Cambios de formatos de archivos.

Cuando corresponda, actualizar:

`docs/03-architecture/data-architecture.md`

y/o

`docs/04-engineering/database.md`


## 12. API DOCUMENTATION

Todo cambio público o interno relevante de API DEBE documentarse.

Registrar:

- Nuevos endpoints.
- Endpoints eliminados.
- Cambios de parámetros.
- Cambios de respuestas.
- Cambios de autenticación.
- Cambios de errores.
- Cambios incompatibles.

Los cambios breaking DEBEN identificarse explícitamente.


## 13. RELEASE DOCUMENTATION

Las versiones importantes pueden documentarse dentro de:

`docs/10-releases/`

Las Release Notes deben resumir:

- Nuevas funcionalidades.
- Cambios importantes.
- Correcciones.
- Breaking changes.
- Seguridad.
- Migraciones necesarias.
- Compatibilidad.

El Release Note NO reemplaza `CHANGELOG.md`.


## 14. TRACEABILITY

Los cambios importantes deben mantener trazabilidad entre:

`Requirement → Feature → Implementation → Test → Documentation`

Cuando sea posible, una funcionalidad debe poder rastrearse desde su requisito hasta su implementación y pruebas.

Ejemplo:

`REQ-001 → FEAT-003 → ADR-002 → implementation → TEST-014`


## 15. DOCUMENTATION QUALITY

Toda documentación debe ser:

- Clara.
- Concisa.
- Técnica cuando corresponda.
- Actualizada.
- Verificable.
- Consistente con el código.
- Comprensible sin necesidad de inspeccionar toda la implementación.

La documentación NO debe limitarse a describir nombres de archivos o funciones.

Debe explicar intención, comportamiento y contexto cuando sea necesario.


## 16. NO HALLUCINATION RULE

Está estrictamente prohibido:

- Inventar funcionalidades.
- Inventar decisiones.
- Inventar métricas.
- Inventar endpoints.
- Inventar modelos.
- Inventar resultados de pruebas.
- Inventar cambios.
- Declarar una implementación que no existe.
- Documentar como terminado algo que solamente fue propuesto.

Diferenciar siempre entre:

`Implemented`
`Proposed`
`Planned`
`Deprecated`
`Removed`

Nunca presentar una propuesta como implementación.


## 17. DOCUMENTATION SYNCHRONIZATION

Cuando una modificación vuelva obsoleta una documentación existente, dicha documentación DEBE actualizarse.

No crear documentación nueva dejando documentos anteriores contradictorios.

Si un documento queda obsoleto:

1. Actualizarlo, o
2. Marcarlo explícitamente como deprecated/obsolete, o
3. Reemplazarlo y registrar la sustitución.

No mantener dos documentos como fuentes contradictorias de verdad.


## 18. SOURCE OF TRUTH

Cuando exista conflicto entre documentación y código:

1. Verificar el estado real del código.
2. Determinar cuál es el comportamiento implementado.
3. Actualizar la documentación para reflejar la realidad.
4. Registrar el cambio en `CHANGELOG.md` cuando corresponda.

La documentación nunca debe utilizarse para ocultar una discrepancia con la implementación.


## 19. FINAL VERIFICATION

Antes de finalizar cualquier tarea DEBES comprobar:

- ¿Se realizaron cambios?
- ¿Todos los cambios relevantes están registrados?
- ¿`CHANGELOG.md` fue actualizado?
- ¿La fecha utiliza `America/Bogota`?
- ¿La fecha tiene formato `YYYY-MM-DD HH:mm`?
- ¿La entrada explica QUÉ cambió?
- ¿La entrada explica POR QUÉ cambió?
- ¿Los documentos técnicos afectados fueron actualizados?
- ¿Existe alguna documentación contradictoria?
- ¿Se crearon ADRs cuando eran necesarios?
- ¿La documentación refleja realmente el estado actual?
- ¿Se inventó accidentalmente alguna información?

Si alguna respuesta es negativa, la tarea NO está terminada.


## 20. REGLA FINAL

El proyecto debe poder responder claramente estas preguntas:

1. ¿Qué estamos construyendo?
2. ¿Por qué lo estamos construyendo?
3. ¿Cómo funciona?
4. ¿Cómo está construido?
5. ¿Por qué fue diseñado de esta manera?
6. ¿Cómo se prueba?
7. ¿Cómo se despliega?
8. ¿Cómo se protege?
9. ¿Qué cambios se han realizado?
10. ¿Cuál es el estado actual?

La documentación debe permitir responderlas sin depender exclusivamente del conocimiento individual de un desarrollador.

DOCUMENTACIÓN = PARTE DEL PRODUCTO.
