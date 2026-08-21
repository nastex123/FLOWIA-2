"""Utility script to reset the admin password in the local SQLite database."""

import sys
import sqlite3
from pathlib import Path

# Add backend directory to sys.path
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.security import hash_password

new_password = sys.argv[1] if len(sys.argv) > 1 else "admin123"
hashed = hash_password(new_password)

# Find all flowmind.db instances (root and backend)
db_paths = [
    root_dir / "data" / "flowmind.db",
    backend_dir / "data" / "flowmind.db",
]

updated_count = 0
for db_path in db_paths:
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET hashed_password = ? WHERE email = ?",
            (hashed, "admin@flowmind.local")
        )
        if cursor.rowcount > 0:
            conn.commit()
            print(f"Base de datos '{db_path.name}' actualizada: contrasena para 'admin@flowmind.local' cambiada a '{new_password}'.")
            updated_count += 1
        conn.close()

if updated_count == 0:
    print("No se encontraron registros de 'admin@flowmind.local' para actualizar.")
