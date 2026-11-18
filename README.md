# EduNexus - Your Personal AI Learning & Productivity Workspace
React + TypeScript + Tailwind frontend, FastAPI backend, SQLite, Ollama.

## Requirements (Windows 11)
Python 3.11+, Node.js 18+, Ollama (https://ollama.com) with `ollama pull llama3.2`. Chrome or Edge for voice.

## Easiest way (VS Code)
Open the `edunexus` folder in VS Code, run `pip install -r backend\requirements.txt` once in the terminal, then open `app.py` and press Run. It builds the frontend on first run and opens the browser.

## Setup (manual)
```
python -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
copy .env.example .env          (set SECRET_KEY to a long random string)
cd frontend
npm install
npm run build
cd ..
uvicorn backend.main:app --port 8000
```
Open http://localhost:8000 (the backend serves the built app).

### Development mode (hot reload)
Terminal 1: `uvicorn backend.main:app --reload --port 8000`
Terminal 2: `cd frontend && npm run dev`, then open http://localhost:5173

## Tests
`python -m pytest -q backend\tests`

## Docs
`docs/ARCHITECTURE.md` (architecture, ER, workflows), `docs/USER_MANUAL.md`, `docs/TESTING.md`, `docs/PROJECT_REPORT.md`.

## Backup
Stop the server, then copy `edunexus.db` and `uploads/`.
