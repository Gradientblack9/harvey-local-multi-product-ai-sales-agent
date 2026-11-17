import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("HARVEY_LOCAL_DATA", str(ROOT / "data"))).resolve()
DB = DATA / "harvey-local.db"
MODEL = os.environ.get("HARVEY_LOCAL_MODEL", "qwen3:4b")
ALLOWED_MODELS = ("qwen3:0.6b", "qwen3:1.7b", "qwen3:4b", "qwen3:8b")
EMBEDDING_PATH = ROOT / "models" / "all-MiniLM-L6-v2"
OLLAMA_URL = "http://127.0.0.1:11434"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
