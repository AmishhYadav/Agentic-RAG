import faiss
import pickle
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from core.config import FAISS_INDEX_PATH, EMBEDDING_MODEL_NAME

class RetrievalAgent:
    """
    Handles similarity search against the FAISS index.
    """
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.index = None
        self.documents = []
        self.sources = []
        self._load_index()

    def _load_index(self):
        """Loads FAISS index and metadata."""
        try:
            index_file = str(FAISS_INDEX_PATH) + ".bin"
            meta_file = str(FAISS_INDEX_PATH) + "_meta.pkl"
            
            self.index = faiss.read_index(index_file)
            with open(meta_file, "rb") as f:
                data = pickle.load(f)
                self.documents = data["documents"]
                self.sources = data["sources"]
        except Exception as e:
            print(f"Warning: Could not load index: {e}")

    def retrieve(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves top-k relevant chunks.
        """
        if not self.index:
            return [{"content": "No index available.", "source": "system"}]

        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding).astype("float32"), k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:
                results.append({
                    "content": self.documents[idx],
                    "source": self.sources[idx],
                    "score": float(distances[0][i])
                })
        
        return results
