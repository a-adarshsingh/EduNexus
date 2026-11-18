import os, tempfile
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/t.db"
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.language import detect, resolve
import backend.services.ollama as ol

def test_language_detection():
    assert detect("Photosynthesis kya hota hai? Mujhe samjhao")[0] == "hinglish"
    assert detect("प्रकाश संश्लेषण क्या है?")[0] == "hi"
    assert detect("What is photosynthesis and how does it work?")[0] == "en"
    assert detect("தாவரங்கள் எப்படி வளரும்")[0] == "ta"
    assert detect("¿Cómo funciona la fotosíntesis?")[0] == "es"
    assert resolve("Explain this in English", "auto") == "en"
    assert resolve("why?", "auto", previous="hi") == "hi"

REG = dict(full_name="Test User", email="a@b.com", password="password123", confirm_password="password123",
           profession="Student", course="MSc CS")

def test_auth_and_isolation(monkeypatch):
    monkeypatch.setattr(ol, "list_models", lambda: ["llama3.2:latest"])
    monkeypatch.setattr(ol.httpx, "post", lambda *a, **k: type("R", (), {
        "raise_for_status": lambda s: None, "json": lambda s: {"message": {"content": "ok"}}})())
    with TestClient(app) as c:
        t1 = c.post("/api/auth/register", json=REG).json()["token"]
        assert c.post("/api/auth/register", json=REG).status_code == 409
        assert c.post("/api/auth/login", json={"email": "a@b.com", "password": "bad"}).status_code == 401
        h1 = {"Authorization": f"Bearer {t1}"}
        r = c.post("/api/chat", json={"message": "प्रकाश संश्लेषण क्या है?"}, headers=h1).json()
        assert r["language"] == "hi"
        t2 = c.post("/api/auth/register", json={**REG, "email": "c@d.com"}).json()["token"]
        h2 = {"Authorization": f"Bearer {t2}"}
        assert c.get(f"/api/conversations/{r['conversation_id']}", headers=h2).status_code == 404
        assert c.get("/api/auth/me").status_code == 401
