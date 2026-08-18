# Base de Datos y Migraciones con Alembic

Este documento describe cómo gestionar el esquema de base de datos de FlowMind AI mediante **Alembic** y **SQLAlchemy 2.0 Asíncrono**.

FlowMind AI usa `AsyncSession` de SQLAlchemy. Alembic está configurado para ejecutarse contra el mismo motor asíncrono, de modo que las migraciones funcionan tanto con SQLite local (`sqlite+aiosqlite`) como con PostgreSQL (`postgresql+asyncpg`).

---

## 1. Estructura de Migraciones

```text
backend/
├── alembic.ini                 # Configuración de Alembic (script_location, URL por defecto)
└── alembic/
    ├── env.py                  # Entorno asíncrono (importa modelos, target_metadata)
    ├── script.py.mako          # Plantilla para nuevas revisiones
    └── versions/               # Revisiones de migración
        └── 3bfc3f0c7da4_initial_schema.py
```

---

## 2. Comandos Habituales

Ejecutar siempre desde el directorio `backend/`:

```bash
# Aplicar todas las migraciones pendientes
python -m alembic upgrade head

# Generar una nueva migración a partir de cambios en los modelos
python -m alembic revision --autogenerate -m "feat: add table_name"

# Ver el historial y la revisión actual
python -m alembic history
python -m alembic current

# Revertir la última migración
python -m alembic downgrade -1
```

---

## 3. Modelos de Dominio y Tablas Principales

1. **`organizations`**: Tenants del sistema (`id`, `name`, `created_at`).
2. **`users`**: Usuarios y credenciales hasheadas con PBKDF2 (`email`, `hashed_password`, `role`).
3. **`documents`**: Documentos subidos y su estado de procesamiento (`filename`, `status`, `organization_id`).
4. **`extraction_records`**: Datos normalizados y estructurados extraídos por documento (`fields_json`, `tables_json`).
5. **`schema_definitions`**: Plantillas canónicas de datos (`fields_schema_json`).
6. **`automation_rules`**: Reglas deterministas de negocio disparadas por eventos (`event`, `operator`, `value`).
7. **`webhook_configs`** & **`webhook_deliveries`**: Integraciones salientes y auditoría de entregas.
