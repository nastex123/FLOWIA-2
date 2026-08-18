#!/usr/bin/env python3
"""Cross-platform unified launcher for FlowMind AI (Backend + PySide6 Desktop UI).

Works natively on Windows, Linux, and macOS with a single command:
    python start.py
"""

import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

# Enable UTF-8 streams on Windows to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Paths
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
DESKTOP_DIR = ROOT_DIR / "desktop"

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    print(f"{CYAN}{BOLD}{'=' * 68}{RESET}")
    print(f"{CYAN}{BOLD}   FlowMind AI -- Unified Suite & Application Launcher{RESET}")
    print(f"{CYAN}{'=' * 68}{RESET}")
    print(f"   {GREEN}* Backend API:{RESET}       http://127.0.0.1:8000")
    print(f"   {GREEN}* Swagger Docs:{RESET}      http://127.0.0.1:8000/docs")
    print(f"   {GREEN}* Desktop Suite (UI):{RESET} PySide6 Native Client (Qt6)")
    print(f"   {GREEN}* Default Admin:{RESET}     admin@flowmind.local / admin123")
    print(f"   {GREEN}* Environment:{RESET}       100% Local & Privacy-First (Zero Cloud)")
    print(f"{CYAN}{'=' * 68}{RESET}\n")


def check_prerequisites():
    """Checks that core directories and dependencies exist."""
    if not BACKEND_DIR.exists():
        print(f"{RED}[ERROR] Backend directory not found at {BACKEND_DIR}{RESET}")
        sys.exit(1)

    try:
        import uvicorn  # noqa
    except ImportError:
        print(f"{RED}[ERROR] 'uvicorn' no está instalado. Ejecuta 'python install.py' primero.{RESET}")
        sys.exit(1)


def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def find_free_port(start_port: int = 8000, max_attempts: int = 50) -> int:
    """Finds the first free TCP port starting from start_port."""
    for p in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", p))
                return p
        except OSError:
            continue
    return start_port


def wait_for_backend(host: str = "127.0.0.1", port: int = 8000, max_wait: float = 8.0) -> bool:
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if is_port_open(host, port):
            return True
        time.sleep(0.3)
    return False


def main():
    print_banner()
    check_prerequisites()

    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR) + (os.pathsep + str(ROOT_DIR)) + (os.pathsep + env.get("PYTHONPATH", ""))

    processes = []
    no_ui = "--no-ui" in sys.argv

    # Determine free port for backend
    port = find_free_port(start_port=8000)
    api_url = f"http://127.0.0.1:{port}"

    try:
        # 1. Start Backend Process (Uvicorn)
        print(f"{CYAN}[1/2] Iniciando FastAPI Backend en {api_url}...{RESET}")
        backend_cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--app-dir",
            str(BACKEND_DIR),
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--reload",
        ]
        backend_proc = subprocess.Popen(
            backend_cmd,
            cwd=str(ROOT_DIR),
            env=env,
        )
        processes.append(backend_proc)

        # Wait for backend to be ready
        print(f"{YELLOW}Esperando a que el backend esté listo en puerto {port}...{RESET}")
        backend_ready = wait_for_backend("127.0.0.1", port)
        if backend_ready:
            print(f"{GREEN}[OK] Backend activo y listo para conexiones.{RESET}\n")
        else:
            print(f"{YELLOW}[WARN] Backend demoró en responder, iniciando UI de todas formas...{RESET}\n")

        # 2. Start Desktop PySide6 UI
        if not no_ui:
            print(f"{CYAN}[2/2] Iniciando Suite de Escritorio PySide6 (UI)...{RESET}")
            desktop_cmd = [sys.executable, str(DESKTOP_DIR / "main.py"), f"--api-url={api_url}"]
            desktop_proc = subprocess.Popen(
                desktop_cmd,
                cwd=str(ROOT_DIR),
                env=env,
            )
            processes.append(desktop_proc)

        print(f"\n{GREEN}{BOLD}[LISTO] FlowMind AI está en ejecución.{RESET}")
        print(f"{YELLOW}Cierra la ventana de la aplicación o pulsa Ctrl+C para detener todo.{RESET}\n")

        # Keep parent alive and monitor child processes
        while True:
            for p in processes:
                poll = p.poll()
                if poll is not None:
                    print(f"\n{YELLOW}[AVISO] Proceso (PID {p.pid}) finalizó (código {poll}). Deteniendo servicios...{RESET}")
                    return
            time.sleep(0.5)

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}[SHUTDOWN] Deteniendo FlowMind AI de forma segura...{RESET}")
    finally:
        for p in processes:
            if p.poll() is None:
                try:
                    if sys.platform == "win32":
                        subprocess.run(
                            ["taskkill", "/F", "/T", "/PID", str(p.pid)],
                            capture_output=True,
                        )
                    else:
                        p.terminate()
                        p.wait(timeout=3)
                except Exception:
                    try:
                        p.kill()
                    except Exception:
                        pass
        print(f"{GREEN}[OK] Todos los servicios de FlowMind AI se detuvieron limpiamente.{RESET}")


if __name__ == "__main__":
    main()
