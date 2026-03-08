import hashlib
import json
import os
from typing import List, Dict, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CHUNK_SIZE = 300
_MODEL = None


def get_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(MODEL_NAME)
    return _MODEL


def split_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    chunks = []
    current = ""

    for line in lines:
        if len(current) + len(line) + 1 <= chunk_size:
            current += line + "\n"
        else:
            if current.strip():
                chunks.append(current.strip())
            current = line + "\n"

    if current.strip():
        chunks.append(current.strip())

    return chunks


def build_signature(docs: List[Dict]) -> str:
    parts = [f"MODEL={MODEL_NAME}", f"CHUNK={CHUNK_SIZE}"]

    for doc in docs:
        file_name = doc["file_name"]
        text_hash = hashlib.md5(doc["text"].encode("utf-8")).hexdigest()
        parts.append(f"{file_name}:{text_hash}")

    raw = "|".join(parts)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def build_vector_store(docs: List[Dict]) -> Tuple[faiss.Index, List[str]]:
    texts = []

    for doc in docs:
        chunks = split_text(doc["text"], CHUNK_SIZE)
        for chunk in chunks:
            if len(chunk) >= 10:
                texts.append(chunk)

    if not texts:
        return None, []

    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=False)
    embeddings = np.asarray(embeddings, dtype="float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    return index, texts


def build_or_load_vector_store(docs: List[Dict], cache_dir: str = "data") -> Tuple[faiss.Index, List[str]]:
    os.makedirs(cache_dir, exist_ok=True)

    vector_path = os.path.join(cache_dir, "vector.index")
    texts_path = os.path.join(cache_dir, "vector_texts.json")
    signature_path = os.path.join(cache_dir, "vector_signature.txt")

    current_signature = build_signature(docs)

    if (
        os.path.exists(vector_path)
        and os.path.exists(texts_path)
        and os.path.exists(signature_path)
    ):
        with open(signature_path, "r", encoding="utf-8") as f:
            saved_signature = f.read().strip()

        if saved_signature == current_signature:
            index = faiss.read_index(vector_path)
            with open(texts_path, "r", encoding="utf-8") as f:
                texts = json.load(f)
            return index, texts

    index, texts = build_vector_store(docs)

    if index is None:
        return None, []

    faiss.write_index(index, vector_path)

    with open(texts_path, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)

    with open(signature_path, "w", encoding="utf-8") as f:
        f.write(current_signature)

    return index, texts


def search_similar(query: str, index, texts: List[str], top_k: int = 3, min_distance: float = 1.5) -> List[str]:
    if index is None or not texts:
        return []

    model = get_model()
    q_emb = model.encode([query], show_progress_bar=False)
    q_emb = np.asarray(q_emb, dtype="float32")

    distances, indices = index.search(q_emb, top_k)

    results = []
    seen = set()

    for dist, idx in zip(distances[0], indices[0]):
        if idx < 0 or idx >= len(texts):
            continue

        text = texts[idx].strip()
        if not text or text in seen:
            continue

        if dist <= min_distance:
            results.append(text)
            seen.add(text)

    return results
