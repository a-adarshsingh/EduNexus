from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database.session import init_db
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from .api import auth, chat, library, tools, planner, account

app = FastAPI(title="EduNexus API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
for r in (chat, library, tools, planner, account): app.include_router(r.router)

@app.on_event("startup")
def startup(): init_db()

@app.get("/api/health")
def health(): return {"status": "ok"}

# Serve the built React app (frontend/dist) from the same server when present.
_dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if _dist.exists():
    app.mount("/", StaticFiles(directory=_dist, html=True), name="web")
