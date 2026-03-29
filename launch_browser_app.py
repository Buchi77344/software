import os
import time
import socket
import threading
import subprocess
import platform
import webbrowser
import urllib.request
import urllib.error

HOST = "127.0.0.1"
PORT = 8010
URL = f"http://{HOST}:{PORT}"
PROJECT_SETTINGS = "cbt.settings"


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
    except Exception:
        return False


def wait_for_server(timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        if is_port_open() and is_http_ready():
            return True
        time.sleep(0.5)
    return False


def run_server():
    try:
        print("Starting Django server...")
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", PROJECT_SETTINGS)
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