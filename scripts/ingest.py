import glob
import os
import pickle
import sys
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
# isort: off
from core.config import DATA_DIR, EMBEDDING_MODEL_NAME, FAISS_INDEX_PATH  # noqa: E402

# isort: on


def ingest_documents():
    """
    Reads text files from data/documents, chunks them, computes embeddings,
    and saves a FAISS index.
    """
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    docs_path = DATA_DIR / "documents" / "*.txt"
    files = glob.glob(str(docs_path))

    if not files:
        print("No documents found in data/documents.")
        return

    documents = []
    doc_sources = []

    print(f"Found {len(files)} documents.")

    # Simple chunking (by line for this demo to avoid complex deps like LangChain)
    # In a real app, use recursive character splitting.
    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            documents.extend(lines)
            doc_sources.extend([os.path.basename(file_path)] * len(lines))

    print(f"Generated {len(documents)} chunks.")

    if not documents:
        print("No content to index.")
        return

    print("Creating embeddings...")
    embeddings = model.encode(documents)

    # Initialize FAISS
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype("float32"))

    # Save Index
    if not os.path.exists(os.path.dirname(FAISS_INDEX_PATH)):
        os.makedirs(os.path.dirname(FAISS_INDEX_PATH))

    faiss.write_index(index, str(FAISS_INDEX_PATH) + ".bin")

    # Save metadata (documents mapping)
    with open(str(FAISS_INDEX_PATH) + "_meta.pkl", "wb") as f:
        pickle.dump({"documents": documents, "sources": doc_sources}, f)

    print(f"Index saved to {FAISS_INDEX_PATH}.bin")
    print("Ingestion complete.")


if __name__ == "__main__":
    ingest_documents()
