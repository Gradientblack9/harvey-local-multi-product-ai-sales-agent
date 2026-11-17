"""Local Sentence Transformers similarity; loading cannot fetch missing model files."""
import threading
from . import config

class EmbeddingsUnavailable(Exception):
    pass

class LocalEmbeddings:
    def __init__(self):
        self.model = None
        self.lock = threading.Lock()

    def similarity(self, icp, prospect):
        with self.lock:
            if not config.EMBEDDING_PATH.is_dir():
                raise EmbeddingsUnavailable("Local embedding model missing. Run scripts/download_embeddings.py during setup.")
            if self.model is None:
                try:
                    from sentence_transformers import SentenceTransformer
                    self.model = SentenceTransformer(str(config.EMBEDDING_PATH),local_files_only=True,device="cpu",trust_remote_code=False)
                except Exception as exc:
                    raise EmbeddingsUnavailable("Cannot load local embedding model: "+str(exc)[:200]) from exc
            vectors = self.model.encode([icp,prospect],normalize_embeddings=True,show_progress_bar=False)
            return round(float(vectors[0] @ vectors[1]),4)
