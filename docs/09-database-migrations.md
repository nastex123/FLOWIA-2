# 09 — Migraciones de Base de Datos con Alembic

Este documento describe cómo gestionar el esquema de base de datos de FlowMind AI mediante **Alembic**.

FlowMind AI usa **SQLAlchemy 2.0 asíncrono** (`AsyncSession`). Alembic está configurado para ejecutarse contra el mismo motor asíncrono, de modo que las migraciones funcionan tanto con SQLite local (`sqlite+aiosqlite`) como con PostgreSQL (`postgresql+asyncpg`).

---

## 1. ¿Qué es Alembic y por qué está aquí?

Alembic es la herramienta oficial de migraciones de SQLAlchemy. Permite versionar y evolucionar el esquema de forma determinista:

* generar migraciones a partir de los modelos (`alembic revision --autogenerate`);
* aplicar migraciones pendientes (`alembic upgrade head`);
* revertir cambios de forma controlada (`alembic downgrade`).

Alembic es **adicional** al arranque actual: `init_db()` en `app/infrastructure/database.py` sigue creando las tablas con `Base.metadata.create_all` si no existen, por lo que el comportamiento de arranque no cambia. En entornos con esquema versionado se recomienda usar Alembic como mecanismo canónico.

---

## 2. Estructura

```text
backend/
├── alembic.ini                 # Configuración de Alembic (script_location, URL por defecto)
└── alembic/
    ├── env.py                  # Entorno asíncrono (importa modelos, target_metadata)
    ├── script.py.mako          # Plantilla para nuevas revisiones
    └── versions/               # Revisiones de migración
        └── <rev>_initial_schema.py
```

Los modelos se importan en `alembic/env.py` desde `app.infrastructure.models`; el `target_metadata` es `Base.metadata` (definido en `app/infrastructure/database.py`).

---

## 3. URL de conexión

`alembic/env.py` resuelve la URL desde la configuración de la aplicación (`app.core.config.settings`), por lo que respeta:

1. la variable de entorno `DATABASE_URL`;
2. el archivo `.env` de la raíz del proyecto (ver `.env.example`);
3. en su defecto, el valor por defecto `sqlite+aiosqlite:///./data/flowmind.db`.

En `alembic.ini` también se declara `sqlalchemy.url` con el mismo valor por defecto como referencia y para modo *offline*.

---

## 4. Comandos habituales

Ejecutar siempre desde el directorio `backend/`:

```bash
# Aplicar todas las migraciones pendientes
python -m alembic upgrade head

# Generar una nueva migración a partir de los cambios en los modelos
python -m alembic revision --autogenerate -m "description del cambio"

# Revisar la migración generada ANTES de aplicarla
python -m alembic upgrade head --sql

# Ver el historial y la revisión actual
python -m alembic history
python -m alembic current

# Revertir la última migración
python -m alembic downgrade -1
```

---

## 5. Flujo de trabajo para cambios de esquema

1. Modificar los modelos en `app/infrastructure/models.py` (o añadir modelos en `app/domain/*.py` que hereden de `Base`).
2. Generar la migración:
   ```bash
   python -m alembic revision --autogenerate -m "feat: add <nueva_tabla>"
   ```
3. **Revisar el archivo generado** en `backend/alembic/versions/` — autogenerate no detecta todos los cambios (p. ej. renames, índices compuestos no estándar). Ajustar `upgrade()` y `downgrade()` cuando sea necesario.
4. Probar la migración:
   ```bash
   python -m alembic upgrade head
   python -m alembic downgrade -1
   python -m alembic upgrade head
   ```
5. Confirmar que la base existente (creada por `init_db()`) es compatible: si ya existían tablas, Alembic las respeta siempre que coincidan con el esquema de los modelos.

---

## 6. Consideraciones

* **Siempre revisar** una migración autogenerada antes de aplicarla. Autogenerate compara contra la base conectada, no contra el estado de otros entornos.
* No editar revisiones ya aplicadas en otros entornos; crear una migración nueva para corregir el esquema.
* Las revisiones deben ser pequeñas y descriptivas (Conventional Commits para el mensaje, p. ej. `migration: add column x to webhook_configs`).
* Nunca incluir secretos ni credenciales reales en las migraciones.