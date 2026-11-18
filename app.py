"""EduNexus launcher. Open this file in VS Code and press Run (the play button).

It will: build the frontend the first time (needs Node.js), start the backend,
and open http://localhost:8000 in your browser.
"""
import os, shutil, subprocess, sys, threading, time, webbrowser
from pathlib import Path

os.environ.setdefault("DISABLE_SQLALCHEMY_CEXT_RUNTIME", "1")
ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
PORT = int(os.getenv("PORT", "8000"))

def check_packages():
    if sys.version_info >= (3, 14):
        print("WARNING: Python %d.%d is very new and some packages may not work. "
              "Use START_EDUNEXUS.bat (it sets up Python 3.12 automatically)." % sys.version_info[:2])
    try:
        import fastapi, uvicorn, sqlalchemy, jwt, httpx, pypdf, multipart  # noqa
        import backend.main  # noqa  (loads everything once so real errors show here)
    except Exception as e:
        sys.exit(f"\nCould not load a required package: {type(e).__name__}: {e}\n"
                 "Please run START_EDUNEXUS.bat (Windows) instead of running app.py directly.\n")

def build_frontend():
    dist = ROOT / "frontend" / "dist" / "index.html"
    if dist.exists():
        return
    npm = shutil.which("npm")
    if not npm:
        sys.exit("\nNode.js is not installed, so the frontend cannot be built.\nInstall Node.js LTS from https://nodejs.org and run app.py again.\n")
    print("First run: building the frontend (this takes 1-2 minutes)...")
    fe = ROOT / "frontend"
    for cmd in ([npm, "install", "--no-audit", "--no-fund"], [npm, "run", "build"]):
        if subprocess.run(cmd, cwd=fe, shell=(os.name == "nt")).returncode != 0:
            sys.exit("\nFrontend build failed. See the messages above.\n")

def open_browser():
    time.sleep(2)
    webbrowser.open(f"http://localhost:{PORT}")

if __name__ == "__main__":
    check_packages()
    build_frontend()
    if not (ROOT / ".env").exists():
        print("Note: no .env file found. Copy .env.example to .env and set SECRET_KEY "
              "(otherwise you will be logged out every time the server restarts).")
    print(f"\nEduNexus is starting at http://localhost:{PORT}  (press Ctrl+C to stop)\n")
    threading.Thread(target=open_browser, daemon=True).start()
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=PORT)
