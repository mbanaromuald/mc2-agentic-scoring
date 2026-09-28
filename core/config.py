import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "data" / "knowledge"
CHROMA_DIR = os.getenv("CHROMA_DIR", str(BASE_DIR / "chroma_db"))

AUTHOR = "Romuald MBANA MEDJO"
ORG = "MC2 · Groupe SAPA (Société Africaine de Participation)"
