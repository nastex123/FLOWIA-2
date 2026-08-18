#!/usr/bin/env python3
"""Cross-platform installation and setup script for FlowMind AI.

Supports Windows, Linux, and macOS.
Sets up the Python virtual environment, installs backend dependencies,
installs Next.js Web Frontend packages (Node.js/npm), initializes environment variables (.env),
and runs verification smoke tests.

Usage:
    python install.py
    python install.py --os windows
    python install.py --os linux
    python install.py --skip-frontend
    python install.py --skip-smoke-test
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

# Enable UTF-8 streams on Windows to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Project directories
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
VENV_DIR = ROOT_DIR / "venv"

# ANSI Colors for terminal output
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    """Displays the FlowMind installer banner."""
    print(f"\n{CYAN}{BOLD}{'=' * 72}{RESET}")
    print(f"{CYAN}{BOLD}   FlowMind AI -- Automated Environment & Dependency Installer{RESET}")
    print(f"{CYAN}{'=' * 72}{RESET}")
    print(f"   {GREEN}* Architecture:{RESET} 100% Local & Privacy-First Suite (Zero Cloud)")
    print(f"   {GREEN}* Backend:{RESET}      FastAPI + Pure Python Local Libraries (Port 8000)")
    print(f"   {GREEN}* Frontend:{RESET}     Next.js 14+ Web App (App Router + Tailwind) (Port 3000)")
    print(f"   {GREEN}* Notice:{RESET}       La interfaz opera como aplicacion web moderna (no ventana GUI)")
    print(f"{CYAN}{'=' * 72}{RESET}\n")


def resolve_os_choice(cli_os: Optional[str]) -> str:
    """Detects or prompts for target operating system."""
    detected = "windows" if sys.platform in ("win32", "cygwin") else "linux"

    if cli_os:
        chosen = cli_os.strip().lower()
        if chosen in ("windows", "win"):
            return "windows"
        elif chosen in ("linux", "macos", "darwin", "unix"):
            return "linux"
        else:
            print(f"{YELLOW}[WARN] Opcion de SO '{cli_os}' no reconocida. Usando deteccion: {detected}{RESET}")
            return detected

    if sys.stdin.isatty():
        print(f"{BOLD}Selecciona el sistema operativo objetivo:{RESET}")
        print(f"  [1] Windows (PowerShell / CMD) {'(Detectado)' if detected == 'windows' else ''}")
        print(f"  [2] Linux / macOS (Bash / Zsh) {'(Detectado)' if detected == 'linux' else ''}")
        try:
            choice = input(f"\nElige una opcion [1/2] o pulsa Enter para autodeteccion ({detected}): ").strip()
            if choice == "1":
                return "windows"
            elif choice == "2":
                return "linux"
        except (KeyboardInterrupt, EOFError):
            print("\nInstalacion cancelada.")
            sys.exit(0)

    return detected


def check_prerequisites(target_os: str) -> None:
    """Verifies Python 3.11+, Git, and Node.js/npm."""
    print(f"{CYAN}[1/6] Verificando requisitos previos del sistema...{RESET}")

    # 1. Python version check
    v = sys.version_info
    py_ver_str = f"{v.major}.{v.minor}.{v.micro}"
    if v.major < 3 or (v.major == 3 and v.minor < 11):
        print(f"{RED}[ERROR] Se requiere Python 3.11 o superior. Version actual: {py_ver_str}{RESET}")
        sys.exit(1)
    print(f"  {GREEN}[OK] Python:{RESET}   v{py_ver_str} ({platform.python_implementation()})")

    # 2. Node.js & npm check
    node_path = shutil.which("node")
    npm_path = shutil.which("npm.cmd" if target_os == "windows" else "npm")
    if node_path and npm_path:
        try:
            node_ver = subprocess.check_output([node_path, "--version"], text=True).strip()
            npm_ver = subprocess.check_output([npm_path, "--version"], text=True).strip()
            print(f"  {GREEN}[OK] Node.js:{RESET}  {node_ver} (npm v{npm_ver})")
        except Exception:
            print(f"  {GREEN}[OK] Node.js:{RESET}  Detectado en PATH")
    else:
        print(f"  {YELLOW}[WARN] Node.js / npm no detectado. Requerido para compilar y ejecutar el frontend Next.js.{RESET}")

    # 3. Git check
    git_path = shutil.which("git")
    if git_path:
        try:
            git_ver = subprocess.check_output([git_path, "--version"], text=True).strip()
            print(f"  {GREEN}[OK] Git:{RESET}      {git_ver}")
        except Exception:
            print(f"  {YELLOW}[OK] Git:{RESET}      Detectado en PATH")
    else:
        print(f"  {YELLOW}[WARN] Git no detectado en PATH (opcional si el repo ya fue descargado){RESET}")


def get_venv_executables(target_os: str) -> Tuple[Path, Path]:
    """Returns the paths to python and pip executables inside the virtualenv."""
    if target_os == "windows":
        py_bin = VENV_DIR / "Scripts" / "python.exe"
        pip_bin = VENV_DIR / "Scripts" / "pip.exe"
    else:
        py_bin = VENV_DIR / "bin" / "python"
        pip_bin = VENV_DIR / "bin" / "pip"
    return py_bin, pip_bin


def setup_virtualenv(target_os: str) -> Tuple[Path, Path]:
    """Creates virtual environment if it does not already exist."""
    print(f"\n{CYAN}[2/6] Configurando entorno virtual de Python ({target_os.upper()})...{RESET}")
    py_bin, pip_bin = get_venv_executables(target_os)

    if not VENV_DIR.exists():
        print(f"  Creando entorno virtual en {VENV_DIR}...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
        print(f"  {GREEN}[OK] Entorno virtual creado exitosamente.{RESET}")
    else:
        print(f"  {GREEN}[OK] Entorno virtual existente detectado en {VENV_DIR}.{RESET}")

    if not py_bin.exists():
        alt_py = VENV_DIR / "Scripts" / "python.exe" if target_os != "windows" else VENV_DIR / "bin" / "python"
        if alt_py.exists():
            py_bin = alt_py
            pip_bin = VENV_DIR / "Scripts" / "pip.exe" if target_os != "windows" else VENV_DIR / "bin" / "pip"

    return py_bin, pip_bin


def install_python_dependencies(py_bin: Path, pip_bin: Path) -> None:
    """Upgrades pip and installs backend packages in editable mode."""
    print(f"\n{CYAN}[3/6] Instalando dependencias de Python (FastAPI Backend + ML Local)...{RESET}")
    print("  Actualizando pip al ultimo nivel...")
    subprocess.run([str(py_bin), "-m", "pip", "install", "--upgrade", "pip"], check=True)

    print("  Instalando paquete 'flowmind-backend' con extras de desarrollo [dev]...")
    cmd = [str(pip_bin), "install", "-e", str(BACKEND_DIR) + "[dev]"]
    subprocess.run(cmd, cwd=str(ROOT_DIR), check=True)
    print(f"  {GREEN}[OK] Dependencias de Python instaladas con exito.{RESET}")


def install_frontend_dependencies(target_os: str) -> None:
    """Installs Next.js web application dependencies via npm."""
    print(f"\n{CYAN}[4/6] Instalando dependencias del Frontend Web (Next.js 14+ & Tailwind)...{RESET}")
    if not FRONTEND_DIR.exists():
        print(f"  {YELLOW}[WARN] Directorio frontend/ no encontrado; omitiendo.{RESET}")
        return

    npm_cmd = "npm.cmd" if target_os == "windows" else "npm"
    if not shutil.which(npm_cmd):
        print(f"  {YELLOW}[WARN] 'npm' no encontrado en el sistema. Ejecuta 'npm install' dentro de frontend/ manualmente.{RESET}")
        return

    print("  Ejecutando 'npm install' en frontend/...")
    try:
        subprocess.run([npm_cmd, "install"], cwd=str(FRONTEND_DIR), check=True)
        print(f"  {GREEN}[OK] Dependencias de Next.js instaladas correctamente.{RESET}")
    except Exception as e:
        print(f"  {RED}[ERROR] Error instalando dependencias de frontend: {e}{RESET}")


def setup_env_file() -> None:
    """Ensures .env exists and is configured for out-of-the-box local SQLite mode."""
    print(f"\n{CYAN}[5/6] Configurando variables de entorno (.env)...{RESET}")
    env_file = ROOT_DIR / ".env"
    env_example = ROOT_DIR / ".env.example"

    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print(f"  {GREEN}[OK] Archivo .env creado a partir de .env.example (Modo SQLite local activado).{RESET}")
        else:
            print(f"  {YELLOW}[WARN] .env.example no encontrado; omitiendo copia.{RESET}")
    else:
        print(f"  {GREEN}[OK] Archivo .env ya existe. Se mantendra la configuracion actual.{RESET}")


def run_smoke_test(py_bin: Path) -> None:
    """Verifies that key Python modules can be imported in the virtualenv."""
    print(f"\n{CYAN}[6/6] Ejecutando Smoke Test de integridad del entorno...{RESET}")
    modules_to_test = [
        ("FastAPI & Uvicorn", "import fastapi, uvicorn"),
        ("Pydantic v2", "import pydantic; assert int(pydantic.__version__.split('.')[0]) >= 2"),
        ("SQLAlchemy & SQLite", "import sqlalchemy, aiosqlite"),
        ("Procesamiento Tabular (Pandas/Openpyxl)", "import pandas, openpyxl"),
        ("Extraccion PDF (PyMuPDF/pdfplumber)", "import fitz, pdfplumber"),
        ("Machine Learning Local (scikit-learn/rapidfuzz)", "import sklearn, rapidfuzz"),
        ("Vision Artificial (OpenCV)", "import cv2"),
        ("Grafo de Hechos (NetworkX)", "import networkx"),
    ]

    all_ok = True
    for label, code in modules_to_test:
        res = subprocess.run([str(py_bin), "-c", code], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  {GREEN}[OK] {label}{RESET}")
        else:
            print(f"  {RED}[FAIL] {label}:{RESET} Fallo importacion: {res.stderr.strip() or res.stdout.strip()}")
            all_ok = False

    if all_ok:
        print(f"\n{GREEN}{BOLD}[LISTO] Todos los componentes criticos fueron verificados con exito.{RESET}")
    else:
        print(f"\n{YELLOW}{BOLD}[WARN] Algunos modulos presentaron advertencias. Revisa los mensajes arriba.{RESET}")


def print_completion_summary(target_os: str) -> None:
    """Prints instructions on how to start the full stack application."""
    print(f"\n{CYAN}{BOLD}{'=' * 72}{RESET}")
    print(f"{GREEN}{BOLD}   [OK] INSTALACION COMPLETADA EXITOSAMENTE{RESET}")
    print(f"{CYAN}{'=' * 72}{RESET}")
    print(f"\n{BOLD}Para iniciar FlowMind AI (Backend FastAPI + Frontend Web Next.js):{RESET}\n")

    if target_os == "windows":
        print(f"  {CYAN}1. Iniciar la aplicacion completa:{RESET}")
        print(f"     {BOLD}python start.py{RESET}\n")
    else:
        print(f"  {CYAN}1. Iniciar la aplicacion completa:{RESET}")
        print(f"     {BOLD}python3 start.py{RESET}\n")

    print(f"  {CYAN}2. Direcciones de acceso local:{RESET}")
    print(f"     * {GREEN}Frontend Web:{RESET}      http://localhost:3000")
    print(f"     * {GREEN}Backend API:{RESET}       http://127.0.0.1:8000")
    print(f"     * {GREEN}Swagger Docs:{RESET}      http://127.0.0.1:8000/docs\n")
    print(f"  {CYAN}3. Opciones de ejecucion avanzada:{RESET}")
    print(f"     {BOLD}python start.py --no-ui{RESET}     (Inicia exclusivamente la API FastAPI)")
    print(f"     {BOLD}.\\scripts\\start_frontend.ps1{RESET} (Inicia exclusivamente el servidor Next.js)")
    print(f"     {BOLD}pytest tests/{RESET}              (Ejecuta la suite de pruebas automatizadas)")
    print(f"{CYAN}{'=' * 72}{RESET}\n")


def main():
    parser = argparse.ArgumentParser(description="Instalador unificado para FlowMind AI.")
    parser.add_argument(
        "--os",
        dest="target_os",
        choices=["windows", "linux", "macos"],
        help="Fuerza el sistema operativo objetivo (windows o linux)",
    )
    parser.add_argument(
        "--skip-frontend",
        action="store_true",
        help="Omite la instalacion de dependencias de Next.js (npm)",
    )
    parser.add_argument(
        "--skip-smoke-test",
        action="store_true",
        help="Omite la prueba de importacion de modulos al final",
    )

    args = parser.parse_args()

    print_banner()
    target_os = resolve_os_choice(args.target_os)
    print(f"  {BOLD}Plataforma seleccionada:{RESET} {target_os.upper()}\n")

    check_prerequisites(target_os)
    py_bin, pip_bin = setup_virtualenv(target_os)
    install_python_dependencies(py_bin, pip_bin)

    if not args.skip_frontend:
        install_frontend_dependencies(target_os)

    setup_env_file()

    if not args.skip_smoke_test:
        py_bin, _ = get_venv_executables(target_os)
        if py_bin.exists():
            run_smoke_test(py_bin)

    print_completion_summary(target_os)


if __name__ == "__main__":
    main()
