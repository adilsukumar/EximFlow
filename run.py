import sys
import os
import socket
import threading
import time
import webbrowser
from pathlib import Path

# Safe console encoding configuration
if sys.platform == "win32":
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# Ensure project root is first in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
else:
    sys.path.remove(str(BASE_DIR))
    sys.path.insert(0, str(BASE_DIR))

# Strip external editable finders from sys.meta_path to prevent module hijacking
for finder in list(sys.meta_path):
    finder_repr = repr(finder).lower()
    if "lightsense" in finder_repr or "nifty" in finder_repr:
        sys.meta_path.remove(finder)

def is_port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', port))
            return True
        except OSError:
            return False

def get_target_port() -> int:
    # 1. Check CLI arguments
    desired_port = None
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg in ("--port", "-p") and i + 1 < len(args):
            try:
                desired_port = int(args[i + 1])
                break
            except ValueError:
                pass
        elif arg.isdigit():
            desired_port = int(arg)
            break

    # 2. Check PORT environment variable
    if not desired_port and os.getenv("PORT"):
        try:
            desired_port = int(os.getenv("PORT"))
        except ValueError:
            pass

    # If desired port is available, use it
    if desired_port and is_port_available(desired_port):
        return desired_port
    elif desired_port:
        print(f"[*] Notice: Port {desired_port} is busy or reserved by Windows. Auto-selecting an open 9000-series port...")

    # 3. Dedicated 9000 series ports (isolated from 8000/8080/5050/3000)
    candidate_ports = [9090, 9091, 9092, 7070, 7777, 5500, 8888]
    for p in candidate_ports:
        if is_port_available(p):
            return p

    return 9090

def auto_open_browser(url: str):
    def _open():
        time.sleep(1.2)
        try:
            webbrowser.open(url)
        except Exception:
            pass
    t = threading.Thread(target=_open, daemon=True)
    t.start()

from app.main import app
import uvicorn

if __name__ == "__main__":
    port = get_target_port()
    local_url = f"http://localhost:{port}"
    alt_url = f"http://127.0.0.1:{port}"

    print("\n" + "="*70)
    print("   🚀 EXIMFLOW AI — AUTONOMOUS OUTBOUND ENGINE")
    print("="*70)
    print(f"[*] Port Series:       9000 Series (Port {port})")
    print(f"[*] Working Directory: {BASE_DIR}")
    print(f"[*] OPEN IN BROWSER:   {local_url}")
    print(f"[*] ALTERNATE URL:     {alt_url}")
    print("="*70)
    print("[*] Launching browser automatically in 1 second...")
    print("="*70 + "\n", flush=True)

    # Launch browser automatically
    auto_open_browser(local_url)

    # Fast, rock-solid startup directly with app instance
    enable_reload = "--reload" in sys.argv
    if enable_reload:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=True,
            reload_dirs=[str(BASE_DIR / "app")],
            app_dir=str(BASE_DIR)
        )
    else:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
