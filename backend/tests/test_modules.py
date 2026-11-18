import os, tempfile
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/m.db"
from fastapi.testclient import TestClient
from backend.main import app
import backend.services.ollama as ol

def reg(c, email):
    r = c.post("/api/auth/register", json=dict(full_name="U One", email=email, password="password123",
               confirm_password="password123", profession="Student", course="BSc"))
    return {"Authorization": "Bearer " + r.json()["token"]}

def test_library_planner_privacy(monkeypatch):
    monkeypatch.setattr(ol, "chat", lambda m, msgs: "MOCK:" + msgs[0]["content"][-60:])
    with TestClient(app) as c:
        h1, h2 = reg(c, "x@y.com"), reg(c, "z@y.com")
        txt = ("Photosynthesis is the process by which plants convert light into chemical energy. " * 5).encode()
        d = c.post("/api/library/upload", files={"file": ("bio.txt", txt)}, headers=h1).json()
        assert d["status"] == "ready"
        assert c.post("/api/library/upload", files={"file": ("a.exe", b"x")}, headers=h1).status_code == 400
        assert c.get(f"/api/library/{d['id']}", headers=h2).status_code == 404       # privacy
        assert c.get("/api/library", headers=h2).json() == []
        s = c.post(f"/api/library/{d['id']}/summarize", json={"mode": "short", "language": "hi"}, headers=h1).json()
        assert "Hindi" in s["summary"] and s["language"] == "hi"                       # language passed to model
        a = c.post(f"/api/library/{d['id']}/ask", json={"question": "प्रकाश संश्लेषण क्या है?"}, headers=h1).json()
        assert a["language"] == "hi" and a["sources"]
        g = c.post(f"/api/library/{d['id']}/generate", json={"kind": "mcq"}, headers=h1)
        assert g.status_code == 200
        t = c.post("/api/planner/tasks", json={"subject": "Bio", "title": "Read ch1", "due_date": "2030-01-01"}, headers=h1).json()
        assert c.patch(f"/api/planner/tasks/{t['id']}", json={"done": True}, headers=h2).status_code == 404
        assert c.patch(f"/api/planner/tasks/{t['id']}", json={"done": True}, headers=h1).json()["done"] is True
        c.post("/api/planner/sessions", json={"subject": "Bio", "minutes": 25}, headers=h1)
        an = c.get("/api/analytics", headers=h1).json()
        assert an["total_minutes"] == 25 and an["tasks_done"] == 1 and an["documents"] == 1
        assert c.get("/api/analytics", headers=h2).json()["total_minutes"] == 0
        r = c.post("/api/tools", json={"kind": "grammar", "text": "he go school"}, headers=h1).json()
        assert r["result"].startswith("MOCK")
        assert c.patch("/api/auth/profile", json={"theme": "dark", "interface_language": "ur"}, headers=h1).json()["theme"] == "dark"
        assert c.delete(f"/api/library/{d['id']}", headers=h1).status_code == 204

def test_docx_without_extra_libs():
    import io, zipfile
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    body = "".join(f"<w:p><w:r><w:t>{t}</w:t></w:r></w:p>" for t in
                   ["Photosynthesis converts light into chemical energy in plants.", "Chlorophyll absorbs red and blue light."])
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("word/document.xml", f'<w:document xmlns:w="{W}"><w:body>{body}</w:body></w:document>')
    with TestClient(app) as c:
        h = reg(c, "docx@y.com")
        d = c.post("/api/library/upload", files={"file": ("n.docx", buf.getvalue())}, headers=h).json()
        assert d["status"] == "ready"
        assert "Chlorophyll" in c.get(f"/api/library/{d['id']}", headers=h).json()["text"]
