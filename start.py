#!/usr/bin/env python3
"""Cross-platform unified launcher for FlowMind AI (Backend + Frontend).

Works natively on Windows, Linux, and macOS with a single command:
    python start.py
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    print(f"{CYAN}{BOLD}{'=' * 65}{RESET}")
    print(f"{CYAN}{BOLD}   🧠 FlowMind AI — Unified Application Launcher{RESET}")
    print(f"{CYAN}{'=' * 65}{RESET}")
    print(f"   {GREEN}▶ Backend API:{RESET}       http://127.0.0.1:8000")
    print(f"   {GREEN}▶ Swagger Docs:{RESET}      http://127.0.0.1:8000/docs")
    print(f"   {GREEN}▶ Web Dashboard:{RESET}     http://localhost:3000")
    print(f"   {GREEN}▶ Default Admin:{RESET}     admin@flowmind.local / admin123")
    print(f"   {GREEN}▶ Environment:{RESET}       100% Local & Privacy-First (Zero Cloud)")
    print(f"{CYAN}{'=' * 65}{RESET}\n")


def check_prerequisites():
    """Checks that Python and npm are accessible."""
    if not BACKEND_DIR.exists():
        print(f"{RED}[ERROR] Backend directory not found at {BACKEND_DIR}{RESET}")
        sys.exit(1)

    if not FRONTEND_DIR.exists():
        print(f"{RED}[ERROR] Frontend directory not found at {FRONTEND_DIR}{RESET}")
        sys.exit(1)

    # Check node_modules
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print(f"{YELLOW}[WARN] 'node_modules' not found in frontend. Running 'npm install'...{RESET}")
        try:
            npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
            subprocess.run([npm_cmd, "install"], cwd=str(FRONTEND_DIR), check=True)
            print(f"{GREEN}[OK] Frontend dependencies installed successfully.{RESET}\n")
        except Exception as e:
            print(f"{RED}[ERROR] Failed to run 'npm install': {e}{RESET}")
            sys.exit(1)


def main():
    print_banner()
    check_prerequisites()

    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR) + (os.pathsep + env.get("PYTHONPATH", ""))

    processes = []

    try:
        # 1. Start Backend Process (Uvicorn)
        print(f"{CYAN}[1/2] Starting FastAPI Backend on port 8000...{RESET}")
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
            "8000",
            "--reload",
        ]
        backend_proc = subprocess.Popen(
            backend_cmd,
            cwd=str(ROOT_DIR),
            env=env,
        )
        processes.append(backend_proc)

        # Brief pause to let backend bind port
        time.sleep(1.5)

        # 2. Start Frontend Process (Next.js)
        print(f"{CYAN}[2/2] Starting Next.js Frontend on port 3000...{RESET}")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        frontend_proc = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=str(FRONTEND_DIR),
            env=os.environ.copy(),
            shell=(sys.platform == "win32"),
        )
        processes.append(frontend_proc)

        print(f"\n{GREEN}{BOLD}[READY] Both services are running!{RESET}")
        print(f"{YELLOW}Press Ctrl+C to stop both servers gracefully.{RESET}\n")

        # Keep parent alive and monitor child processes
        while True:
            for p in processes:
                poll = p.poll()
                if poll is not None:
                    print(f"\n{YELLOW}[NOTICE] Process (PID {p.pid}) exited with code {poll}. Stopping remaining services...{RESET}")
                    return
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}[SHUTDOWN] Received Ctrl+C. Gracefully stopping FlowMind AI...{RESET}")
    finally:
        for p in processes:
            if p.poll() is None:
                try:
                    if sys.platform == "win32":
                        # Terminate process tree on Windows
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
        print(f"{GREEN}[OK] All FlowMind AI services stopped cleanly.{RESET}")


if __name__ == "__main__":
    main()
