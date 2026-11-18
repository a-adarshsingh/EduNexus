import os, secrets, warnings
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    warnings.warn("SECRET_KEY not set: using a temporary key, logins reset on restart.")
    SECRET_KEY = secrets.token_urlsafe(48)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./edunexus.db")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.2")
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "720"))
