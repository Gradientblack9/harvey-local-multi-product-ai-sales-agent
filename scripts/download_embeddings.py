"""Explicit, setup-only model download. The running app never executes this script."""
import os
from pathlib import Path
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ.pop("HF_HUB_OFFLINE",None)
os.environ.pop("TRANSFORMERS_OFFLINE",None)
from sentence_transformers import SentenceTransformer
target = Path(__file__).resolve().parents[1] / "models" / "all-MiniLM-L6-v2"
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2",device="cpu",trust_remote_code=False)
model.save(str(target))
print("Embedding model saved locally.",flush=True)
