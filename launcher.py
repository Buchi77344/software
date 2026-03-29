import os
import sys
import time
import socket
import threading
import subprocess
import platform
import webbrowser
import urllib.request
import urllib.error
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8010
START_PATH = "/"   # change this only if your real first page is different
URL = f"http://{HOST}:{PORT}{START_PATH}"
PROJECT_SETTINGS = "cbt.settings"


def get_data_dir():
    """
    Writable folder for database/media when app is packaged with PyInstaller.
    """
    if getattr(sys, "frozen", False):
        base = Path(os.getenv("LOCALAPPDATA", Path.home()))
        data_dir = base / "cbt"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    return Path(__file__).resolve().parent


def copy_bundled_db_if_needed():
    """
    If db.sqlite3 was bundled into the EXE, copy it once to the writable data dir.
    """
    try:
        if getattr(sys, "frozen", False):
            bundled_base = Path(getattr(sys, "_MEIPASS"))
            bundled_db = bundled_base / "db.sqlite3"
            target_db = get_data_dir() / "db.sqlite3"

            if bundled_db.exists() and not target_db.exists():
                import shutil
                shutil.copy2(bundled_db, target_db)
                print(f"Copied bundled database to: {target_db}")
    except Exception as e:
        print("Database copy warning:")
        print(e)


def is_port_open(host=HOST, port=PORT):
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def is_http_ready(url=URL):
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return response.status in (200, 301, 302, 403)
    except urllib.error.HTTPError as e:
        # If Django responds at all, the server is up.
        return e.code in (200, 301, 302, 403, 404)
    except Exception:
        return False


def wait_for_server(timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        if is_port_open() and is_http_ready():
            return True
        time.sleep(0.5)
    return False


def run_migrations():
    try:
        print("Running migrations...")
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", PROJECT_SETTINGS)

        import django
        django.setup()

        from django.core.management import call_command
        call_command("migrate", interactive=False, run_syncdb=True)
        print("Migrations completed successfully.")
    except Exception as e:
        print("Migration failed:")
        print(e)
        raise


def collect_static():
    try:
        print("Collecting static files...")
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", PROJECT_SETTINGS)

        import django
        django.setup()

        from django.core.management import call_command
        call_command("collectstatic", interactive=False, verbosity=0, clear=False)
        print("Static files collected successfully.")
    except Exception as e:
        print("Collectstatic warning:")
        print(e)


def run_server():
    try:
        print("Starting Django server...")
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", PROJECT_SETTINGS)

        copy_bundled_db_if_needed()
        run_migrations()
        collect_static()

        from cbt.wsgi import application
        from waitress import serve

        serve(
            application,
            host=HOST,
            port=PORT,
            threads=6,
        )
    except Exception as e:
        print("Server failed to start:")
        print(e)


def open_windows_browser():
    edge_candidates = [
        "msedge",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]

    for edge in edge_candidates:
        try:
            print(f"Trying Edge: {edge}")
            subprocess.Popen([
                edge,
                "--kiosk",
                URL,
                "--edge-kiosk-type=fullscreen",
                "--no-first-run",
            ])
            return True
        except Exception:
            continue

    chrome_candidates = [
        "chrome",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]

    for chrome in chrome_candidates:
        try:
            print(f"Trying Chrome: {chrome}")
            subprocess.Popen([
                chrome,
                "--start-fullscreen",
                URL,
            ])
            return True
        except Exception:
            continue

    print("Falling back to default browser...")
    return webbrowser.open(URL)


def open_non_windows_browser():
    system = platform.system()

    try:
        if system == "Linux":
            print("Opening browser on Linux...")
            subprocess.Popen(["xdg-open", URL])
            return True
        elif system == "Darwin":
            print("Opening browser on macOS...")
            subprocess.Popen(["open", URL])
            return True
        else:
            return webbrowser.open(URL)
    except Exception:
        return webbrowser.open(URL)


def open_browser():
    if platform.system() == "Windows":
        return open_windows_browser()
    return open_non_windows_browser()


if __name__ == "__main__":
    print(f"Using URL: {URL}")
    print(f"Data directory: {get_data_dir()}")

    if is_port_open():
        print(f"Port {PORT} is already in use.")
        print("Make sure it is your Django app, or stop the old process first.")
    else:
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

    print("Waiting for server to become ready...")

    if not wait_for_server():
        raise RuntimeError(f"Server did not become ready at {URL}")

    print("Server is ready.")
    print("Opening browser...")

    if not open_browser():
        raise RuntimeError("Could not open a browser.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down launcher...")